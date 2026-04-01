<p align="center">
  <img src="assets/logo.png" alt="Tacet" width="300">
</p>

Real-time voice dictation that types your words into any active window. Quietly, accurately, and without fuss.

[![Sponsor](https://img.shields.io/badge/Sponsor-❤-ea4aaa)](https://github.com/sponsors/revoltbots-com)
![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-blue)
![Python](https://img.shields.io/badge/python-3.9%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)

## What is Tacet?

Tacet is a speech-to-text app that listens to your microphone and types what you say directly into whatever window you're working in. Your text editor, browser, email, Slack, whatever. No clipboard, no copy-paste, no app-specific plugins.

It runs fully offline using local AI models, or connects to OpenAI/Deepgram if you prefer cloud. You pick.

The name comes from the musical term *tacet*, which means "be silent." It's the direction on a score that tells a musician to wait, then come in.

## Features

- Real-time transcription with live preview
- Multiple transcription engines: local (faster-whisper), OpenAI API, Deepgram API
- Voice commands you can customize (actions triggered by speech)
- Word replacements for abbreviation expansion
- Templates for reusable text blocks
- Timestamp insertion
- Session history and usage statistics
- Multi-language UI (English, Spanish, French, German)
- System tray integration
- Cross-platform: Windows, macOS, Linux
- Fully offline mode with no data leaving your machine

## Quick start

```bash
git clone https://github.com/revoltbots-com/tacet-voice.git
cd tacet-voice
cp config.example.json config.json
pip install -r requirements.txt
python main.py
```

## Transcription engines

| Engine | Type | Pros | Cons |
|---|---|---|---|
| Local (faster-whisper) | Offline | Free, private, no API key needed | Needs model download, slower on CPU |
| OpenAI API | Cloud | High accuracy, fast | Needs API key, costs money |
| Deepgram API | Cloud | Fast, real-time optimized | Needs API key, costs money |

## Configuration

Copy `config.example.json` to `config.json` before first run. The main things you'll want to change:

- `engine` - set to `"local"`, `"openai"`, or `"deepgram"`
- `hotkey` - your activation shortcut (default: `ctrl+shift+d`)
- `audio.sound_device` - microphone device ID (0 for system default)
- `gui.ui_language` - UI language (`en`, `es`, `fr`, `de`)

You can also change most of these from the Settings panel inside the app.

## Voice commands

Voice commands let you trigger actions by speaking. A few examples:

- Say "new line" to insert a line break
- Say "period" or "full stop" to insert punctuation
- Say "delete that" to remove the last transcribed chunk

You can add, remove, or change these in Settings > Voice Commands.

## Supported languages

The UI is available in English, Spanish, French, and German. The transcription language (what you actually speak) is configured separately and depends on the engine.

## Contributing

Contributions are welcome. See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on bugs, features, and pull requests.

## License

MIT License. Copyright (c) 2025-2026 Revolt Bots LLC.

## Acknowledgments

Tacet builds on solid open-source work:

- [faster-whisper](https://github.com/guillaumekln/faster-whisper) for the optimized Whisper implementation
- [OpenAI Whisper](https://github.com/openai/whisper) for the speech recognition model
- [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter) for the UI framework
- [sounddevice](https://github.com/spatialaudio/python-sounddevice) for audio capture
- [pynput](https://github.com/moses-palmer/pynput) for keyboard control

---

<p align="center">
  <img src="assets/revoltbots.png" alt="Revolt Bots" width="80">
  <br>
  by <a href="https://revoltbots.com/en/products/tacet?ref=gh-tacet">RevoltBots.com</a>
</p>
