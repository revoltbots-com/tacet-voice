"""
Dictation Engine

Main orchestration class that coordinates all transcription components.
"""

import json
import os
import queue
import threading
import time
from collections import deque
from typing import Optional, Dict, Callable, Tuple

import numpy as np
import sounddevice as sd
from pynput import keyboard
from pynput.keyboard import Controller

# Import from our modular structure
from tacet.engine.providers import LocalEngine, OpenAIEngine, DeepgramEngine
from tacet.engine.processors import (
    VoiceCommandProcessor,
    TextReplacementProcessor,
    AutoPunctuationProcessor,
    TimestampProcessor,
    TemplateProcessor,
)
from tacet.engine.tracking import UsageStatsTracker, SessionHistoryManager
from tacet.engine.utils.audio import resolve_input_device, write_wav
from tacet.engine.utils.keyboard import normalize_hotkey, backspace, MODIFIER_KEYS
from tacet.engine.utils.text import postprocess


class DictationEngine:
    """
    Main dictation engine that coordinates transcription, processing, and output.

    Handles:
    - Audio capture via sounddevice
    - Voice Activity Detection (VAD)
    - Transcription via multiple providers (Local, OpenAI, Deepgram)
    - Text processing (voice commands, replacements, timestamps, etc.)
    - Keyboard output and clipboard management
    - Usage statistics and session history
    """

    def __init__(self, config_path: str, callbacks: Optional[Dict[str, Callable]] = None):
        """
        Initialize the dictation engine.

        Args:
            config_path: Path to config.json file
            callbacks: Dict with optional callback functions:
                - 'on_status_change': func(status: str) - "idle", "listening", "transcribing"
                - 'on_preview_update': func(text: str) - Real-time partial transcription
                - 'on_final_text': func(text: str) - Final transcribed text
                - 'on_error': func(error: str) - Error messages
        """
        self.config_path = config_path
        self.callbacks = callbacks or {}

        # Load config
        with open(config_path, "r", encoding="utf-8") as f:
            self.config = json.load(f)

        # Extract config sections
        self.hotkey_user = self.config.get("hotkey", "ctrl+a")
        self.hotkey = normalize_hotkey(self.hotkey_user)

        engine_name = (self.config.get("engine") or "local").lower()
        self.engine_name = engine_name
        local_cfg = self.config.get("local", {})
        openai_cfg = self.config.get("openai", {})
        deepgram_cfg = self.config.get("deepgram", {})
        audio_cfg = self.config.get("audio", {})
        self.typing_cfg = self.config.get("typing", {})
        cont_cfg = self.config.get("continuous", {})
        live_cfg = self.config.get("live", {})
        behavior_cfg = self.config.get("behavior", {})
        clipboard_cfg = self.config.get("clipboard", {})

        self.stop_on_any_keypress = bool(behavior_cfg.get("stop_on_any_keypress", True))
        self.clipboard_enabled = bool(clipboard_cfg.get("enabled", True))
        self.clipboard_mode = clipboard_cfg.get("mode", "replace")  # "replace" or "append"
        self.hotkey_guard_sec = float(behavior_cfg.get("hotkey_guard_sec", 0.8))
        self.debug_levels = bool(behavior_cfg.get("debug_levels", False))

        # Initialize voice command processor
        voice_commands_cfg = self.config.get("voice_commands", {})
        self.voice_processor = VoiceCommandProcessor(voice_commands_cfg)

        # Initialize text replacement processor
        repl_cfg = self._build_replacements_config(self.config)
        self._log(f"Replacement config: enabled={repl_cfg.get('enabled')}, "
                  f"count={len(repl_cfg.get('replacements', {}))}")
        self.replacement_processor = TextReplacementProcessor(repl_cfg)

        # Initialize usage stats tracker
        here = os.path.dirname(os.path.abspath(config_path))
        stats_path = os.path.join(here, "stats.json")
        self.stats_tracker = UsageStatsTracker(stats_path)

        # Initialize feature processors
        auto_punct_cfg = self.config.get("auto_punctuation", {})
        self.auto_punct_processor = AutoPunctuationProcessor(auto_punct_cfg)

        timestamp_cfg = self.config.get("timestamps", {})
        self.timestamp_processor = TimestampProcessor(timestamp_cfg)

        template_cfg = self.config.get("templates", {})
        self.template_processor = TemplateProcessor(template_cfg)

        session_history_cfg = self.config.get("session_history", {})
        self.session_history = SessionHistoryManager(session_history_cfg, here)

        # Dictation tuning
        self.silence_ms = int(cont_cfg.get("silence_ms", 450))
        self.min_chunk_ms = int(cont_cfg.get("min_chunk_ms", 250))
        self.energy_threshold = float(cont_cfg.get("energy_threshold", 0.003))
        self.preroll_ms = int(cont_cfg.get("preroll_ms", 250))
        self.idle_timeout_sec = float(cont_cfg.get("idle_timeout_sec", 60))

        # Live preview tuning
        self.live_enabled = bool(live_cfg.get("enabled", True))
        self.update_interval_ms = int(live_cfg.get("update_interval_ms", 900))
        self.max_preview_chars = int(live_cfg.get("max_preview_chars", 400))
        self.max_partial_seconds = float(live_cfg.get("max_partial_seconds", 8.0))

        self.sr = int(audio_cfg.get("sample_rate", 48000))
        self.ch = int(audio_cfg.get("channels", 1))

        self.kb = Controller()

        # Initialize engines
        self.local_engine = None
        self.openai_engine = None
        self.deepgram_engine = None

        if engine_name == "local":
            requested_model = local_cfg.get("model", "tiny")
            self._log(f"Loading local model: {requested_model} ...")
            self.local_engine = LocalEngine(
                model_name=requested_model,
                device=local_cfg.get("device", "cpu"),
                compute_type=local_cfg.get("compute_type", "int8"),
            )
            self.local_cfg = local_cfg

            # Speed test on startup: if model is too slow, fall back to tiny
            if requested_model not in ("tiny",):
                self._log(f"Running speed test for {requested_model} ...")
                silence = np.zeros(int(audio_cfg.get("sample_rate", 48000)), dtype=np.float32)
                test_wav = write_wav(silence, int(audio_cfg.get("sample_rate", 48000)))
                t0 = time.time()
                try:
                    self.local_engine.transcribe(
                        test_wav,
                        language=local_cfg.get("language", None),
                        task=local_cfg.get("task", "transcribe"),
                    )
                finally:
                    try:
                        os.remove(test_wav)
                    except OSError:
                        pass
                elapsed = time.time() - t0
                self._log(f"Speed test: {elapsed:.1f}s for 1s audio")

                if elapsed > 5.0:
                    self._log(f"Model '{requested_model}' too slow ({elapsed:.1f}s), falling back to tiny")
                    self.local_engine = LocalEngine(
                        model_name="tiny",
                        device=local_cfg.get("device", "cpu"),
                        compute_type=local_cfg.get("compute_type", "int8"),
                    )
                    local_cfg["model"] = "tiny"
                    self.config["local"]["model"] = "tiny"
                    try:
                        with open(self.config_path, "w", encoding="utf-8") as f:
                            json.dump(self.config, f, indent=2)
                    except Exception:
                        pass
        elif engine_name == "openai":
            env_name = openai_cfg.get("api_key_env", "OPENAI_API_KEY")
            api_key = os.environ.get(env_name)
            if not api_key:
                raise RuntimeError(f"Missing API key env var: {env_name}")
            self.openai_engine = OpenAIEngine(
                base_url=openai_cfg.get("base_url", "https://api.openai.com/v1"),
                model=openai_cfg.get("model", "whisper-1"),
                api_key=api_key,
            )
            self.openai_cfg = openai_cfg
        elif engine_name == "deepgram":
            env_name = deepgram_cfg.get("api_key_env", "DEEPGRAM_API_KEY")
            api_key = os.environ.get(env_name)
            if not api_key:
                raise RuntimeError(f"Missing API key env var: {env_name}")
            self.deepgram_engine = DeepgramEngine(
                api_key=api_key,
                model=deepgram_cfg.get("model", "nova-2"),
            )
            self.deepgram_cfg = deepgram_cfg
        else:
            raise ValueError("engine must be 'local', 'openai', or 'deepgram'")

        # Shared state
        self.state_lock = threading.Lock()
        self.listening = threading.Event()
        self.last_toggle_time = 0.0
        self.ignore_keypress_until = 0.0
        self.last_voice_time = time.time()

        # Utterance tracking
        self.current_utt_id = 0
        self.current_seq = 0
        self.applied_seq = 0
        self.preview_len = 0
        self._last_preview_text = ""
        self._stopped = False

        # Dictation loop state (shared so _stop_dictation can flush)
        self._speaking = False
        self._blocks = []
        self._blocks_lock = threading.Lock()

        # Queues
        self.audio_q: "queue.Queue[np.ndarray]" = queue.Queue(maxsize=600)
        self.tx_q: "queue.Queue[Tuple[int, int, bool, str]]" = queue.Queue()

        # Session tracking for auto-save
        self.session_text_buffer = []
        self.session_start_time = None

        # Initialize audio stream
        self._init_audio_stream(audio_cfg)

        # Start worker threads
        self._start_workers()

        # Start keyboard listener for stop-on-keypress
        if self.stop_on_any_keypress:
            keyboard.Listener(on_press=self._on_keypress, suppress=False).start()

        self._log(f"Engine initialized [{engine_name}]")
        self._call_callback('on_status_change', 'idle')

    @staticmethod
    def _build_replacements_config(config: dict) -> dict:
        """
        Build a flat TextReplacementProcessor-compatible config from the
        ``word_replacements`` section (written by the GUI).  Falls back to
        ``custom_replacements`` when ``word_replacements`` is absent so that
        existing hand-edited configs keep working.
        """
        word_repl = config.get("word_replacements")
        if word_repl is not None:
            # New GUI format: merge all enabled language dictionaries
            enabled = bool(word_repl.get("enabled", True))
            case_sensitive = bool(word_repl.get("case_sensitive", False))
            merged: dict = {}
            for lang_dict in word_repl.get("dictionaries", {}).values():
                if lang_dict.get("enabled", False):
                    merged.update(lang_dict.get("replacements", {}))
            return {
                "enabled": enabled,
                "case_sensitive": case_sensitive,
                "replacements": merged,
            }

        # Legacy fallback
        return config.get("custom_replacements", {})

    def _log(self, message: str):
        """Internal logging"""
        try:
            print(message)
        except UnicodeEncodeError:
            # Windows console can't handle emojis, strip them
            print(message.encode('ascii', 'ignore').decode('ascii'))

    def _call_callback(self, name: str, *args):
        """Call a callback if it exists"""
        if name in self.callbacks and self.callbacks[name]:
            try:
                self.callbacks[name](*args)
            except Exception as e:
                self._log(f"Callback error ({name}): {repr(e)}")

    def _init_audio_stream(self, audio_cfg: dict):
        """Initialize audio input stream"""
        dev = resolve_input_device(audio_cfg)

        try:
            if isinstance(dev, int):
                dev_name = sd.query_devices(dev, "input")["name"]
                self._log(f"Using input device: [{dev}] {dev_name}")
            elif isinstance(dev, str):
                self._log(f"Using input device (by name): {dev}")
            else:
                default_in = sd.default.device[0]
                default_name = sd.query_devices(default_in, "input")["name"]
                self._log(f"Using default input device: [{default_in}] {default_name}")
        except Exception:
            self._log("Could not print device name.")

        try:
            self.stream = sd.InputStream(
                samplerate=self.sr,
                channels=self.ch,
                dtype="float32",
                device=dev,
                callback=self._audio_callback,
            )
            self.stream.start()
        except Exception as e:
            self._log("\nFailed to open microphone input stream.")
            self._log(f"Reason: {repr(e)}")
            self._call_callback('on_error', f"Failed to open microphone: {repr(e)}")
            raise

    def _audio_callback(self, indata, frames, time_info, status):
        """Audio stream callback"""
        if not self.listening.is_set():
            return
        try:
            self.audio_q.put_nowait(indata.copy())
        except queue.Full:
            pass

    def _safe_type(self, text: str):
        """Type text with keypress ignore window"""
        self.ignore_keypress_until = time.time() + min(2.5, 0.25 + 0.01 * len(text))

        per_key_delay = float(self.typing_cfg.get("per_key_delay_sec", 0.0))
        if per_key_delay <= 0:
            self.kb.type(text)
        else:
            for c in text:
                self.kb.press(c)
                self.kb.release(c)
                time.sleep(per_key_delay)

    def _apply_live_text(self, new_text: str):
        """Apply live preview text (with backspacing)"""
        new_text = (new_text or "")[:self.max_preview_chars]
        if self.preview_len > 0:
            backspace(self.kb, self.preview_len)
        self._safe_type(new_text)
        self.preview_len = len(new_text)
        self._last_preview_text = new_text

        # Also update UI
        self._call_callback('on_preview_update', new_text)

    def _commit_final_text(self, final_text: str):
        """Commit final text (removing preview)"""
        if self.preview_len > 0:
            backspace(self.kb, self.preview_len)

        out = postprocess(
            final_text,
            remove_trailing_period=bool(self.typing_cfg.get("remove_trailing_period", False)),
            add_trailing_space=bool(self.typing_cfg.get("add_trailing_space", True)),
        )

        # Process voice commands (period, comma, newline, delete, etc.)
        out = self.voice_processor.process_text(out)

        # Process timestamp insertion (e.g., "insert timestamp" -> "14:30:45")
        out = self.timestamp_processor.process_text(out)

        # Expand templates (e.g., "greeting" -> "Dear Sir or Madam,\n\n")
        out = self.template_processor.process_text(out)

        # Auto-punctuation (smart capitals after sentences)
        out = self.auto_punct_processor.process_text(out)

        # Apply custom word replacements (last step)
        before_repl = out
        out = self.replacement_processor.process_text(out)
        if out != before_repl:
            self._log(f"Replacement: '{before_repl.strip()}' -> '{out.strip()}'")

        self._safe_type(out)
        self._last_preview_text = ""

        # Copy to clipboard if enabled
        if self.clipboard_enabled:
            try:
                import pyperclip
                if self.clipboard_mode == "append":
                    existing = pyperclip.paste()
                    pyperclip.copy(existing + out)
                else:
                    pyperclip.copy(out)
            except Exception as e:
                self._log(f"⚠️ Clipboard copy failed: {e}")

        self.preview_len = 0

        # Track usage statistics
        self.stats_tracker.record_text(out)

        # Auto-save session if enabled
        if self.session_history and self.session_history.auto_save:
            self.session_text_buffer.append(out)

            # Build metadata
            metadata = {
                "engine": self.config.get("engine", "local"),
                "model": self.config.get("local", {}).get("model", "unknown"),
                "language": self.config.get("local", {}).get("language") or "auto"
            }

            # Save accumulated session text
            full_text = " ".join(self.session_text_buffer)
            self.session_history.save_session(full_text, metadata)

        self._log(f"✅ {final_text}")
        self._call_callback('on_final_text', out)

    def _tx_worker(self):
        """Transcription worker thread"""
        while True:
            utt_id, seq, is_final, wav_path = self.tx_q.get()
            try:
                kind = "FINAL" if is_final else "partial"
                self._log(f"[TX] Got {kind} utt={utt_id} seq={seq}")
                self._call_callback('on_status_change', 'transcribing')

                # Transcribe
                if self.local_engine:
                    text = self.local_engine.transcribe(
                        wav_path,
                        language=self.local_cfg.get("language", None),
                        task=self.local_cfg.get("task", "transcribe"),
                    )
                elif self.openai_engine:
                    text = self.openai_engine.transcribe(
                        wav_path,
                        language=self.openai_cfg.get("language", None),
                    )
                elif self.deepgram_engine:
                    text = self.deepgram_engine.transcribe(
                        wav_path,
                        language=self.deepgram_cfg.get("language", None),
                    )

                if not text:
                    self._log(f"[TX] Empty result, skipping")
                    continue

                with self.state_lock:
                    live_utt = self.current_utt_id

                # Stale result? Discard
                if utt_id != live_utt:
                    self._log(f"[TX] Stale: utt={utt_id} != live={live_utt}, discarding")
                    continue

                if not is_final:
                    # Don't apply partials after dictation stopped
                    if self._stopped:
                        self._log(f"[TX] Stopped, discarding partial")
                        continue

                    with self.state_lock:
                        if seq <= self.applied_seq:
                            continue
                        self.applied_seq = seq

                    if self.live_enabled:
                        self._apply_live_text(text)
                else:
                    self._log(f"[TX] Committing final: '{text[:50]}'")
                    self._commit_final_text(text)

                    # Update status back to listening if still active
                    if self.listening.is_set():
                        self._call_callback('on_status_change', 'listening')

            except Exception as e:
                self._log(f"Transcription worker error: {repr(e)}")
                self._call_callback('on_error', f"Transcription error: {repr(e)}")
            finally:
                try:
                    os.remove(wav_path)
                except OSError:
                    pass
                self.tx_q.task_done()

    def _start_workers(self):
        """Start transcription worker threads"""
        for _ in range(2):
            threading.Thread(target=self._tx_worker, daemon=True).start()

    def _dictation_loop(self):
        """Main dictation loop (VAD processing)"""
        block_ms = 20
        block_len = int(self.sr * (block_ms / 1000.0))

        preroll = deque(maxlen=max(1, int((self.preroll_ms / 1000.0) * self.sr / block_len)))

        silence_count = 0

        min_samples = int(self.sr * (self.min_chunk_ms / 1000.0))
        silence_samples_needed = int(self.sr * (self.silence_ms / 1000.0))

        update_interval_sec = self.update_interval_ms / 1000.0
        last_update = time.time()
        last_level_print = time.time()

        while True:
            if self.listening.is_set():
                if (time.time() - self.last_voice_time) > self.idle_timeout_sec:
                    self._stop_dictation(f"idle timeout {self.idle_timeout_sec:.1f}s")
                    time.sleep(0.05)
                    continue

            try:
                buf = self.audio_q.get(timeout=0.2)
            except queue.Empty:
                continue

            x = buf.reshape(-1).astype(np.float32)
            if len(x) == 0:
                self.audio_q.task_done()
                continue

            if self.listening.is_set():
                rms = float(np.sqrt(np.mean(x * x) + 1e-12))
                preroll.append(x)

                if self.debug_levels and (time.time() - last_level_print) > 1.0:
                    self._log(f"🔊 level={rms:.5f} threshold={self.energy_threshold:.5f}")
                    last_level_print = time.time()

                if rms >= self.energy_threshold:
                    self.last_voice_time = time.time()
                    if not self._speaking:
                        self._speaking = True
                        silence_count = 0
                        with self._blocks_lock:
                            self._blocks = list(preroll)

                        with self.state_lock:
                            self.current_utt_id += 1
                            self.current_seq = 0
                            self.applied_seq = 0

                        self.preview_len = 0
                        last_update = time.time()

                    with self._blocks_lock:
                        self._blocks.append(x)

                    # Partial update
                    if self.live_enabled and (time.time() - last_update) >= update_interval_sec:
                        last_update = time.time()

                        max_blocks = int((self.max_partial_seconds * self.sr) / block_len)
                        with self._blocks_lock:
                            recent = self._blocks[-max_blocks:] if max_blocks > 0 else list(self._blocks)
                        samples = np.concatenate(recent, axis=0)

                        if len(samples) >= min_samples:
                            wav = write_wav(samples, self.sr)
                            with self.state_lock:
                                utt_id = self.current_utt_id
                                self.current_seq += 1
                                seq = self.current_seq
                            self.tx_q.put((utt_id, seq, False, wav))

                else:
                    if self._speaking:
                        with self._blocks_lock:
                            self._blocks.append(x)
                        silence_count += len(x)

                        # Silence ended the utterance
                        if silence_count >= silence_samples_needed:
                            self._speaking = False
                            silence_count = 0

                            with self._blocks_lock:
                                samples = np.concatenate(self._blocks, axis=0) if self._blocks else np.array([], dtype=np.float32)
                                self._blocks = []

                            if len(samples) >= min_samples:
                                wav = write_wav(samples, self.sr)
                                with self.state_lock:
                                    utt_id = self.current_utt_id
                                    self.current_seq += 1
                                    seq = self.current_seq
                                # Clear preview tracking — the worker will commit final
                                self._last_preview_text = ""
                                self.tx_q.put((utt_id, seq, True, wav))

            self.audio_q.task_done()

    def _on_keypress(self, key):
        """Keyboard listener for stop-on-keypress"""
        if not self.stop_on_any_keypress or not self.listening.is_set():
            return

        now = time.time()

        # Ignore hotkey press/release aftermath
        if now - self.last_toggle_time < self.hotkey_guard_sec:
            return

        # Ignore our own injected keystrokes
        if now < self.ignore_keypress_until:
            return

        # Ignore modifier-only presses
        if key in MODIFIER_KEYS:
            return

        self._stop_dictation("key pressed")

    def _stop_dictation(self, reason: str):
        """Internal stop dictation"""
        if self.listening.is_set():
            self.listening.clear()
            self.last_toggle_time = time.time()

            # Block new partials from tx_workers but let finals through
            self._stopped = True

            # Flush any pending audio blocks as a final transcription
            with self._blocks_lock:
                pending_blocks = list(self._blocks)
                self._blocks = []
            self._speaking = False

            if pending_blocks:
                samples = np.concatenate(pending_blocks, axis=0)
                min_samples = int(self.sr * (self.min_chunk_ms / 1000.0))
                if len(samples) >= min_samples:
                    self._log(f"[STOP] Flushing {len(samples)} audio samples as final")
                    wav = write_wav(samples, self.sr)
                    with self.state_lock:
                        utt_id = self.current_utt_id
                        self.current_seq += 1
                        seq = self.current_seq
                    self.tx_q.put((utt_id, seq, True, wav))
            elif self._last_preview_text:
                # No audio blocks but we have a preview — commit it
                self._log(f"[STOP] Committing preview: '{self._last_preview_text[:50]}'")
                self._commit_final_text(self._last_preview_text)

            # Reset session tracking for next session
            self.session_text_buffer = []
            self.session_start_time = None

            self._log(f"Dictation stopped ({reason}).")
            self._call_callback('on_status_change', 'idle')

    def start_listening(self):
        """Start dictation"""
        if self.listening.is_set():
            return

        # Flush audio queue
        while not self.audio_q.empty():
            try:
                self.audio_q.get_nowait()
                self.audio_q.task_done()
            except queue.Empty:
                break

        self.preview_len = 0
        self._stopped = False
        self.last_voice_time = time.time()
        self.listening.set()
        self.last_toggle_time = time.time()
        self.ignore_keypress_until = time.time() + self.hotkey_guard_sec

        # Track session start for auto-save
        if self.session_start_time is None:
            self.session_start_time = time.time()

        self._log(f"🎙️ Live dictation started [{self.engine_name}]")
        self._call_callback('on_status_change', 'listening')

    def stop_listening(self):
        """Stop dictation"""
        self._stop_dictation("manual")

    def toggle_listening(self):
        """Toggle dictation on/off"""
        if self.listening.is_set():
            self.stop_listening()
        else:
            self.start_listening()

    def is_listening(self) -> bool:
        """Check if currently listening"""
        return self.listening.is_set()

    def get_hotkey(self) -> str:
        """Get normalized hotkey string"""
        return self.hotkey

    def get_hotkey_display(self) -> str:
        """Get user-friendly hotkey display"""
        return self.hotkey_user

    def set_device(self, device_id: int):
        """Change microphone device"""
        was_listening = self.listening.is_set()

        if was_listening:
            self.stop_listening()

        # Stop and close old stream
        self.stream.stop()
        self.stream.close()

        # Create new stream
        try:
            self.stream = sd.InputStream(
                samplerate=self.sr,
                channels=self.ch,
                dtype="float32",
                device=device_id,
                callback=self._audio_callback,
            )
            self.stream.start()

            # Update config
            self.config['audio']['sound_device'] = device_id
            self._save_config()

            dev_name = sd.query_devices(device_id, "input")["name"]
            self._log(f"Switched to device: [{device_id}] {dev_name}")

            if was_listening:
                self.start_listening()

        except Exception as e:
            self._log(f"Failed to switch device: {repr(e)}")
            self._call_callback('on_error', f"Failed to switch device: {repr(e)}")
            raise

    def update_config(self, new_config: dict):
        """Update configuration and reload engine"""
        prev_stop_on_any_keypress = self.stop_on_any_keypress
        previous_model = self.local_cfg.get("model") if hasattr(self, "local_cfg") else None

        self.config = new_config

        self.local_cfg = new_config.get("local", self.local_cfg)
        self.openai_cfg = new_config.get("openai", getattr(self, "openai_cfg", {}))
        self.deepgram_cfg = new_config.get("deepgram", getattr(self, "deepgram_cfg", {}))
        self.typing_cfg = new_config.get("typing", self.typing_cfg)

        behavior_cfg = new_config.get("behavior", {})
        clipboard_cfg = new_config.get("clipboard", {})
        cont_cfg = new_config.get("continuous", {})
        live_cfg = new_config.get("live", {})

        self.stop_on_any_keypress = bool(behavior_cfg.get("stop_on_any_keypress", self.stop_on_any_keypress))
        self.clipboard_enabled = bool(clipboard_cfg.get("enabled", self.clipboard_enabled))
        self.clipboard_mode = clipboard_cfg.get("mode", self.clipboard_mode)
        self.hotkey_guard_sec = float(behavior_cfg.get("hotkey_guard_sec", self.hotkey_guard_sec))
        self.debug_levels = bool(behavior_cfg.get("debug_levels", self.debug_levels))
        self.silence_ms = int(cont_cfg.get("silence_ms", 450))
        self.min_chunk_ms = int(cont_cfg.get("min_chunk_ms", 250))
        self.energy_threshold = float(cont_cfg.get("energy_threshold", 0.003))
        self.preroll_ms = int(cont_cfg.get("preroll_ms", 250))
        self.idle_timeout_sec = float(cont_cfg.get("idle_timeout_sec", self.idle_timeout_sec))
        self.live_enabled = bool(live_cfg.get("enabled", self.live_enabled))
        self.update_interval_ms = int(live_cfg.get("update_interval_ms", 900))
        self.max_preview_chars = int(live_cfg.get("max_preview_chars", self.max_preview_chars))
        self.max_partial_seconds = float(live_cfg.get("max_partial_seconds", self.max_partial_seconds))

        self.voice_processor = VoiceCommandProcessor(new_config.get("voice_commands", {}))
        self.auto_punct_processor = AutoPunctuationProcessor(new_config.get("auto_punctuation", {}))
        self.timestamp_processor = TimestampProcessor(new_config.get("timestamps", {}))
        self.template_processor = TemplateProcessor(new_config.get("templates", {}))

        # Reload text replacement processor with the updated config
        repl_cfg = self._build_replacements_config(new_config)
        self._log(f"Replacement config: enabled={repl_cfg.get('enabled')}, "
                  f"count={len(repl_cfg.get('replacements', {}))}")
        self.replacement_processor = TextReplacementProcessor(repl_cfg)

        here = os.path.dirname(os.path.abspath(self.config_path))
        self.session_history = SessionHistoryManager(new_config.get("session_history", {}), here)

        # Attempt model reload BEFORE saving config to disk.
        # If reload fails, revert the model in config so we don't persist a broken state.
        new_model = self.local_cfg.get("model", previous_model)
        if self.local_engine and new_model != previous_model:
            try:
                self.reload_model(new_model)
            except Exception:
                # Revert model in config so the saved file keeps the working model
                self._log(f"Model reload failed, reverting to: {previous_model}")
                self.local_cfg["model"] = previous_model
                new_config["local"]["model"] = previous_model

        self._save_config()

        if self.stop_on_any_keypress and not prev_stop_on_any_keypress:
            keyboard.Listener(on_press=self._on_keypress, suppress=False).start()

        self._log("Configuration updated")

    def reload_model(self, model_name: str):
        """Reload the model (for local engine only).

        Raises on failure so the caller can revert config.
        The old local_engine is preserved if the new one fails to load.
        Runs a speed test after loading — raises if too slow for real-time.
        """
        if self.local_engine is None:
            return

        was_listening = self.listening.is_set()
        if was_listening:
            self.stop_listening()

        try:
            self._log(f"Loading model: {model_name} ...")
            self._call_callback('on_status_change', 'loading')

            new_engine = LocalEngine(
                model_name=model_name,
                device=self.local_cfg.get("device", "cpu"),
                compute_type=self.local_cfg.get("compute_type", "int8"),
            )

            # Speed test: transcribe 1 second of silence, must complete in < 5s
            self._log(f"Running speed test for {model_name} ...")
            silence = np.zeros(self.sr, dtype=np.float32)  # 1 second
            test_wav = write_wav(silence, self.sr)
            t0 = time.time()
            try:
                new_engine.transcribe(
                    test_wav,
                    language=self.local_cfg.get("language", None),
                    task=self.local_cfg.get("task", "transcribe"),
                )
            finally:
                try:
                    os.remove(test_wav)
                except OSError:
                    pass
            elapsed = time.time() - t0
            self._log(f"Speed test: {elapsed:.1f}s for 1s audio")

            if elapsed > 5.0:
                raise RuntimeError(
                    f"Model '{model_name}' is too slow for real-time dictation "
                    f"({elapsed:.1f}s to transcribe 1s of audio). "
                    f"Use 'tiny' or 'base' on CPU, or switch to CUDA."
                )

            # Only replace engine on success
            self.local_engine = new_engine

            self._log(f"Model loaded: {model_name}")
            self._call_callback('on_status_change', 'idle')

            if was_listening:
                self.start_listening()

        except Exception as e:
            self._log(f"Failed to load model: {repr(e)}")
            self._call_callback('on_error', f"Failed to load model {model_name}: {repr(e)}")
            self._call_callback('on_status_change', 'idle')
            raise

    def _save_config(self):
        """Save configuration to file"""
        try:
            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            self._log(f"Failed to save config: {repr(e)}")

    def save_config(self):
        """Public method to save configuration"""
        self._save_config()

    def start(self):
        """Start the dictation loop thread"""
        threading.Thread(target=self._dictation_loop, daemon=True).start()

    def shutdown(self):
        """Clean shutdown"""
        self._log("Shutting down...")
        self.stop_listening()

        if hasattr(self, 'stream'):
            self.stream.stop()
            self.stream.close()

        # Save usage statistics
        if hasattr(self, 'stats_tracker'):
            self.stats_tracker.end_session()
