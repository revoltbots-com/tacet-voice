# Contributing to Tacet

Thank you for your interest in contributing! This document provides guidelines for contributing to the project.

## How to Contribute

### Reporting Bugs

If you find a bug, please create an issue with:
- Clear description of the bug
- Steps to reproduce
- Expected vs actual behavior
- Your environment (OS, Python version, model used)
- Any error messages or logs

### Suggesting Features

Feature suggestions are welcome! Please create an issue with:
- Clear description of the feature
- Use case / why it would be useful
- Any implementation ideas (optional)

### Pull Requests

1. **Fork the repository**
   ```bash
   git clone https://github.com/yourusername/tacet-voice.git
   cd tacet-voice
   ```

2. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Make your changes**
   - Follow the existing code style
   - Add comments for complex logic
   - Test your changes on your platform

4. **Test thoroughly**
   - Test on your platform (Windows/macOS/Linux)
   - Try different models if changing transcription logic
   - Test both GUI and CLI modes if applicable

5. **Commit your changes**
   ```bash
   git add .
   git commit -m "Add feature: description"
   ```

6. **Push and create PR**
   ```bash
   git push origin feature/your-feature-name
   ```
   Then create a Pull Request on GitHub

## Code Style

- Use meaningful variable and function names
- Add docstrings to functions and classes
- Follow PEP 8 style guide
- Keep lines under 100 characters when possible
- Use type hints where helpful

## Project Structure

```
tacet/
├── engine/                 # Backend transcription engine
├── gui/                    # Frontend GUI application
├── config.json             # User configuration (gitignored)
├── config.example.json     # Template configuration
└── requirements.txt        # Python dependencies
```

## Key Components

### DictationEngine (dictation_engine.py)
- Core transcription logic
- Audio capture and VAD
- Thread management
- Callbacks for UI updates

### TranscriptionGUI (stt_gui.py)
- CustomTkinter UI
- Settings dialog
- Queue-based thread communication
- Hotkey integration

## Testing

Currently, testing is manual. Before submitting a PR:

1. **Test basic functionality**
   - Start/stop dictation
   - Hotkey works
   - Text appears correctly
   - Settings save properly

2. **Test edge cases**
   - Very short audio clips
   - Long silence periods
   - Rapid start/stop
   - Device switching

3. **Test on your platform**
   - Windows, macOS, or Linux
   - Note any platform-specific issues

## Areas for Contribution

Here are some areas where contributions would be especially welcome:

### Features
- [ ] Automatic punctuation
- [ ] Custom word replacement (e.g., "gmail dot com" → "gmail.com")
- [ ] Keyboard shortcuts for common actions
- [ ] System tray icon / minimize to tray
- [ ] Auto-start on boot option
- [ ] Support for more languages
- [ ] Noise reduction / audio preprocessing
- [ ] Alternative TTS engines (Azure, Google Cloud)

### Improvements
- [ ] Automated tests
- [ ] Performance profiling
- [ ] Better error handling
- [ ] Logging system
- [ ] User preferences UI improvements
- [ ] Installer/package scripts (MSI, DMG, DEB)

### Documentation
- [ ] Video tutorial
- [ ] Screenshots for README
- [ ] API documentation
- [ ] Troubleshooting guide improvements

### Platform Support
- [ ] macOS testing and fixes
- [ ] Linux desktop integration
- [ ] Raspberry Pi support
- [ ] ARM architecture support

## Questions?

If you have questions about contributing, feel free to:
- Open an issue
- Ask in discussions
- Contact the maintainers

## Code of Conduct

- Be respectful and inclusive
- Provide constructive feedback
- Help others learn and grow
- Focus on the technical merits

Thank you for contributing!
