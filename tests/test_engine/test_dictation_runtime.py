"""Runtime behavior tests for the dictation engine."""

import copy
import json
from pathlib import Path
import shutil
from uuid import uuid4

from tacet.engine.dictation import DictationEngine
from tacet.gui.dialogs.word_replacements import WordReplacementsDialog


class DummyLocalEngine:
    """Lightweight stand-in for the local transcription engine."""

    def __init__(self, *args, **kwargs):
        pass


def _build_engine(monkeypatch, sample_config, callbacks=None):
    config = copy.deepcopy(sample_config)
    config["word_replacements"] = {
        "enabled": True,
        "case_sensitive": False,
        "dictionaries": {
            "en": {
                "enabled": True,
                "replacements": {
                    "btw": "by the way",
                    "add my email": "tfrisch@clickup.com",
                },
            },
            "es": {"enabled": False, "replacements": {}},
            "fr": {"enabled": False, "replacements": {}},
            "de": {"enabled": False, "replacements": {}},
        },
    }
    config["templates"] = {"enabled": False, "snippets": {}}
    config["timestamps"] = {"enabled": False}
    config["auto_punctuation"] = {"enabled": False}
    config["session_history"] = {"enabled": False, "auto_save": False}

    config_dir = Path(__file__).resolve().parents[1] / "_runtime_tmp" / uuid4().hex
    config_dir.mkdir(parents=True, exist_ok=True)

    config_path = config_dir / "config.json"
    config_path.write_text(json.dumps(config), encoding="utf-8")

    monkeypatch.setattr("tacet.engine.dictation.LocalEngine", DummyLocalEngine)
    monkeypatch.setattr(DictationEngine, "_init_audio_stream", lambda self, cfg: None)
    monkeypatch.setattr(DictationEngine, "_start_workers", lambda self: None)

    return DictationEngine(str(config_path), callbacks=callbacks or {}), config_dir


def test_commit_final_callback_uses_processed_text(monkeypatch, sample_config):
    seen = {}

    def on_final_text(text):
        seen["callback"] = text

    engine, config_dir = _build_engine(
        monkeypatch,
        sample_config,
        callbacks={"on_final_text": on_final_text},
    )
    try:
        engine._safe_type = lambda text: seen.setdefault("typed", text)
        engine.clipboard_enabled = False
        engine.session_history = None

        engine._commit_final_text("please add my email btw")

        assert seen["typed"] == "please tfrisch@clickup.com by the way "
        assert seen["callback"] == seen["typed"]
    finally:
        shutil.rmtree(config_dir, ignore_errors=True)


def test_update_config_refreshes_runtime_transcription_settings(monkeypatch, sample_config):
    engine, config_dir = _build_engine(monkeypatch, sample_config)

    try:
        new_config = copy.deepcopy(engine.config)
        new_config["local"]["language"] = "fr"
        new_config["typing"]["remove_trailing_period"] = True
        new_config["voice_commands"]["enabled"] = False

        engine.update_config(new_config)

        assert engine.local_cfg["language"] == "fr"
        assert engine.typing_cfg["remove_trailing_period"] is True
        assert engine.voice_processor.enabled is False
    finally:
        shutil.rmtree(config_dir, ignore_errors=True)


def test_word_replacements_dialog_normalizes_legacy_config(sample_config):
    config = copy.deepcopy(sample_config)

    assert "word_replacements" not in config

    word_cfg = WordReplacementsDialog._normalize_word_replacements_config(config)

    assert word_cfg["enabled"] == config["custom_replacements"]["enabled"]
    assert word_cfg["case_sensitive"] == config["custom_replacements"]["case_sensitive"]
    assert word_cfg["dictionaries"]["en"]["replacements"] == config["custom_replacements"]["replacements"]
