# Tacet - Architecture Documentation

Version: 2.0.0
Last Updated: 2025-12-16

## Table of Contents

1. [Overview](#overview)
2. [Design Principles](#design-principles)
3. [Package Structure](#package-structure)
4. [Import Hierarchy](#import-hierarchy)
5. [Core Components](#core-components)
6. [Extension Guide](#extension-guide)
7. [Testing](#testing)

---

## Overview

Tacet is a professional, cross-platform speech-to-text application with a modular architecture. The codebase has been refactored from a monolithic structure (6,217 lines in 2 files) to a well-organized package (~50 files, each 20-500 lines).

### Key Stats

- **Total Files**: ~50 Python modules
- **Package Structure**: 8-level import hierarchy
- **Test Coverage**: Integration tests for all modules
- **Lines of Code**: ~6,000 (well-organized)
- **Python Version**: 3.8+

### Architecture Goals

- **Maintainability**: Each file has a single, clear purpose
- **Extensibility**: Easy to add new providers, processors, or dialogs
- **Testability**: Clear boundaries for unit and integration tests
- **Professional Quality**: Follows Python package conventions (similar to Django, Flask)

---

## Design Principles

### 1. Separation of Concerns

The codebase is divided into two main packages:

- **`engine/`**: Backend transcription logic (no GUI dependencies)
- **`gui/`**: Frontend user interface (depends on engine)

This allows the engine to be used independently (e.g., in CLI scripts or other GUIs).

### 2. Single Responsibility

Each module has one clear purpose:
- `audio.py`: Audio device management only
- `voice_commands.py`: Voice command processing only
- `settings.py`: Settings dialog only

### 3. Dependency Injection

Components receive their dependencies via constructor parameters, making them testable:

```python
# Engine receives providers and processors
engine = DictationEngine(
    config_path=config_path,
    callbacks={...}
)

# Dialogs receive parent window and engine
dialog = SettingsDialog(parent_window, engine)
```

### 4. Callback Pattern

Engine-to-GUI communication uses callbacks to avoid tight coupling:

```python
engine = DictationEngine(
    callbacks={
        'on_status_change': lambda status: update_ui(status),
        'on_final_text': lambda text: insert_text(text),
    }
)
```

---

## Package Structure

### Complete Directory Tree

```
tacet/
├── __init__.py                           # Package root (exports DictationEngine, TranscriptionGUI)
│
├── engine/                               # Backend package
│   ├── __init__.py                       # Engine exports
│   ├── base.py                           # BaseEngine interface (abstract class)
│   ├── dictation.py                      # DictationEngine main orchestrator (~700 lines)
│   │
│   ├── providers/                        # Transcription providers
│   │   ├── __init__.py                   # Provider exports
│   │   ├── local.py                      # LocalEngine (faster-whisper)
│   │   ├── openai.py                     # OpenAIEngine (API)
│   │   └── deepgram.py                   # DeepgramEngine (API)
│   │
│   ├── processors/                       # Text processors (pipeline)
│   │   ├── __init__.py                   # Processor exports
│   │   ├── voice_commands.py             # VoiceCommandProcessor (period, comma, new line, etc.)
│   │   ├── text_replacement.py           # TextReplacementProcessor (abbreviations)
│   │   ├── auto_punctuation.py           # AutoPunctuationProcessor (smart capitalization)
│   │   ├── timestamp.py                  # TimestampProcessor (insert timestamps)
│   │   └── template.py                   # TemplateProcessor (expand snippets)
│   │
│   ├── utils/                            # Engine utilities
│   │   ├── __init__.py                   # Utility exports
│   │   ├── audio.py                      # Audio device enumeration and management
│   │   ├── keyboard.py                   # Keyboard control (typing, backspace)
│   │   └── text.py                       # Text postprocessing utilities
│   │
│   └── tracking/                         # Usage tracking
│       ├── __init__.py                   # Tracking exports
│       ├── stats.py                      # UsageStatsTracker (words, time saved)
│       └── session.py                    # SessionHistoryManager (save/load sessions)
│
└── gui/                                  # Frontend package
    ├── __init__.py                       # GUI exports
    ├── app.py                            # TranscriptionGUI main window (~350 lines)
    │
    ├── core/                             # Core GUI components
    │   ├── __init__.py                   # Core exports
    │   ├── translation.py                # TranslationManager (i18n, singleton)
    │   └── system_tray.py                # TrayIcon (system tray integration)
    │
    ├── dialogs/                          # Dialog windows
    │   ├── __init__.py                   # Dialog exports (all 9 dialogs)
    │   ├── base.py                       # BaseDialog (shared functionality)
    │   ├── settings.py                   # SettingsDialog (~250 lines, tabbed)
    │   ├── voice_commands.py             # VoiceCommandsDialog
    │   ├── word_replacements.py          # WordReplacementsDialog
    │   ├── templates.py                  # TemplatesDialog
    │   ├── session_history.py            # SessionHistoryDialog
    │   ├── statistics.py                 # StatisticsDialog
    │   ├── about.py                      # AboutDialog
    │   ├── shortcuts.py                  # ShortcutsDialog
    │   └── export.py                     # ExportDialog
    │
    └── utils/                            # GUI utilities
        ├── __init__.py                   # Utility exports
        ├── platform_utils.py             # Platform detection (IS_MAC, IS_WINDOWS)
        ├── shortcuts.py                  # Keyboard shortcut normalization
        ├── autostart.py                  # Cross-platform auto-start (~170 lines)
        └── icons.py                      # Icon helpers
```

---

## Import Hierarchy

The 8-level import hierarchy prevents circular dependencies by ensuring lower-level modules never import from higher levels.

### Hierarchy Levels

```
Level 1: Core Utilities (no dependencies)
├── tacet.engine.utils.*
└── tacet.gui.utils.*

Level 2: Base Classes and Interfaces
├── tacet.engine.base
└── tacet.gui.core.translation

Level 3: Providers and Processors (use base + utils)
├── tacet.engine.providers.*
├── tacet.engine.processors.*
└── tacet.engine.tracking.*

Level 4: Main Engine (orchestrates providers + processors)
└── tacet.engine.dictation

Level 5: GUI Dialogs (use engine, translation, utils)
├── tacet.gui.dialogs.base
└── tacet.gui.dialogs.*

Level 6: GUI Core (uses dialogs, engine)
└── tacet.gui.core.system_tray

Level 7: Main Application (uses everything)
└── tacet.gui.app

Level 8: Entry Point
└── main.py
```

### Import Rules

1. **Downward only**: Modules can only import from lower levels
2. **No skipping**: Level 4 shouldn't directly import from Level 1 (use Level 2 or 3)
3. **Singletons**: Shared resources use singleton pattern (e.g., `get_translator()`)

### Example Import Patterns

```python
# Level 1: Utils (no internal imports)
# tacet/engine/utils/audio.py
import sounddevice as sd

def list_input_devices():
    # Pure utility function
    pass

# Level 3: Provider (imports base + utils)
# tacet/engine/providers/local.py
from tacet.engine.base import BaseEngine
from tacet.engine.utils.text import postprocess

class LocalEngine(BaseEngine):
    # Implements interface
    pass

# Level 7: Main app (imports dialogs, engine)
# tacet/gui/app.py
from tacet.engine.dictation import DictationEngine
from tacet.gui.dialogs import SettingsDialog
from tacet.gui.core.translation import get_translator

class TranscriptionGUI(ctk.CTk):
    # Uses everything
    pass
```

---

## Core Components

### Engine Components

#### DictationEngine (`engine/dictation.py`)

**Purpose**: Main orchestrator for transcription workflow

**Responsibilities**:
- Audio capture via sounddevice
- Voice Activity Detection (VAD)
- Provider selection and management
- Text processor pipeline execution
- Callback invocation for GUI updates
- Threading and queue management

**Key Methods**:
```python
engine = DictationEngine(config_path, callbacks)
engine.start()                  # Start background threads
engine.start_listening()        # Begin capturing audio
engine.stop_listening()         # Stop capturing
engine.toggle_listening()       # Toggle on/off
engine.set_device(device_id)    # Change microphone
engine.shutdown()               # Clean shutdown
```

#### BaseEngine (`engine/base.py`)

**Purpose**: Abstract interface for transcription providers

**Contract**:
```python
class BaseEngine(ABC):
    @abstractmethod
    def transcribe(self, wav_path: str, language: Optional[str] = None, **kwargs) -> str:
        """Transcribe audio file to text"""
        pass
```

**Implementations**:
- `LocalEngine`: faster-whisper (offline)
- `OpenAIEngine`: OpenAI Whisper API
- `DeepgramEngine`: Deepgram API

#### Processors (`engine/processors/`)

**Purpose**: Text transformation pipeline

**Flow**: Raw transcription → Voice Commands → Replacements → Auto-Punctuation → Timestamps → Templates → Final Text

**Adding a New Processor**:
```python
# 1. Create tacet/engine/processors/my_processor.py
class MyProcessor:
    def __init__(self, config):
        self.enabled = config.get('enabled', False)

    def process(self, text: str) -> str:
        if not self.enabled:
            return text
        # Transform text
        return transformed_text

# 2. Import in engine/processors/__init__.py
from tacet.engine.processors.my_processor import MyProcessor
__all__ = [..., "MyProcessor"]

# 3. Instantiate in engine/dictation.py
self.my_processor = MyProcessor(self.config.get('my_processor', {}))

# 4. Add to pipeline in _process_text()
text = self.my_processor.process(text)
```

### GUI Components

#### TranscriptionGUI (`gui/app.py`)

**Purpose**: Main application window

**Responsibilities**:
- Create UI layout (status, microphone dropdown, buttons, text area)
- Initialize DictationEngine with callbacks
- Process UI update queue (thread-safe)
- Handle keyboard shortcuts
- Open dialog windows
- System tray integration

**UI Update Pattern**:
```python
# Engine runs in background thread
self.engine = DictationEngine(
    callbacks={
        'on_status_change': lambda s: self.ui_queue.put(("status", s)),
        'on_final_text': lambda t: self.ui_queue.put(("final", t)),
    }
)

# UI thread processes queue
def process_ui_queue(self):
    while not self.ui_queue.empty():
        msg_type, data = self.ui_queue.get_nowait()
        if msg_type == "status":
            self._update_status(data)
        elif msg_type == "final":
            self._commit_final(data)
    self.after(50, self.process_ui_queue)  # Schedule next check
```

#### BaseDialog (`gui/dialogs/base.py`)

**Purpose**: Shared functionality for all dialogs

**Provides**:
- Standard initialization (title, size, modality)
- Icon setting
- Window centering on parent
- Transient window setup

**Usage**:
```python
class MyDialog(BaseDialog):
    def __init__(self, parent):
        super().__init__(parent, title="My Dialog", size="600x400")
        # Add widgets
```

#### TranslationManager (`gui/core/translation.py`)

**Purpose**: Internationalization (i18n)

**Features**:
- Load translations from `languages.json`
- Nested key access (`"buttons.save"`)
- Variable substitution (`"{count} items"`)
- Singleton pattern

**Usage**:
```python
from tacet.gui.core.translation import get_translator

translator = get_translator()
text = translator.t('buttons.save')  # "Save"
text = translator.t('stats.words', count=42)  # "42 words transcribed"
```

---

## Extension Guide

### Adding a New Transcription Provider

1. **Create provider file**: `tacet/engine/providers/my_provider.py`

```python
from tacet.engine.base import BaseEngine
from typing import Optional

class MyProviderEngine(BaseEngine):
    def __init__(self, config):
        self.config = config
        self.api_key = config.get('api_key', '')
        # Initialize your provider

    def transcribe(self, wav_path: str, language: Optional[str] = None, **kwargs) -> str:
        # Read audio file
        # Call your provider's API
        # Return transcribed text
        return "transcribed text"
```

2. **Export in `__init__.py`**:

```python
# engine/providers/__init__.py
from tacet.engine.providers.my_provider import MyProviderEngine
__all__ = ["LocalEngine", "OpenAIEngine", "DeepgramEngine", "MyProviderEngine"]
```

3. **Add to DictationEngine**:

```python
# engine/dictation.py
from tacet.engine.providers import LocalEngine, OpenAIEngine, DeepgramEngine, MyProviderEngine

def _initialize_transcription_engine(self):
    engine_type = self.config.get('engine', {}).get('type', 'local')

    if engine_type == 'my_provider':
        self.transcription_engine = MyProviderEngine(self.config.get('my_provider', {}))
    # ... existing providers
```

4. **Add to config.json**:

```json
{
  "engine": {
    "type": "my_provider"
  },
  "my_provider": {
    "api_key": "your-key-here",
    "model": "default"
  }
}
```

### Adding a New Dialog

1. **Create dialog file**: `tacet/gui/dialogs/my_dialog.py`

```python
import customtkinter as ctk
from tacet.gui.dialogs.base import BaseDialog
from tacet.gui.core.translation import get_translator

_translator = get_translator()

class MyDialog(BaseDialog):
    def __init__(self, parent):
        super().__init__(parent, title=_translator.t('my_dialog.title'), size="500x400")

        # Main frame
        main_frame = ctk.CTkFrame(self)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Add your widgets
        ctk.CTkLabel(main_frame, text="My Dialog Content").pack(pady=20)

        # Buttons
        button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        button_frame.pack(fill="x")

        ctk.CTkButton(button_frame, text=_translator.t('buttons.close'),
                     command=self.destroy, width=100).pack(side="left", padx=5)
```

2. **Export in `__init__.py`**:

```python
# gui/dialogs/__init__.py
from tacet.gui.dialogs.my_dialog import MyDialog
__all__ = [..., "MyDialog"]
```

3. **Add menu button in app.py**:

```python
# gui/app.py
from tacet.gui.dialogs import MyDialog

def _create_menu_bar(self):
    buttons = [
        (_translator.t('buttons.settings'), self._open_settings),
        (_translator.t('buttons.my_dialog'), self._open_my_dialog),  # Add this
    ]

def _open_my_dialog(self):
    MyDialog(self)
```

4. **Add translations**:

```json
// languages.json
{
  "en": {
    "buttons": {
      "my_dialog": "My Dialog"
    },
    "my_dialog": {
      "title": "My Custom Dialog"
    }
  }
}
```

### Adding a New Utility Function

1. **Choose appropriate location**:
   - Engine utility: `tacet/engine/utils/`
   - GUI utility: `tacet/gui/utils/`

2. **Create or add to existing file**:

```python
# tacet/gui/utils/helpers.py
def my_utility_function(param):
    """Helpful description"""
    # Implementation
    return result
```

3. **Export in `__init__.py`**:

```python
# gui/utils/__init__.py
from tacet.gui.utils.helpers import my_utility_function
__all__ = [..., "my_utility_function"]
```

4. **Use in other modules**:

```python
from tacet.gui.utils import my_utility_function

result = my_utility_function(data)
```

---

## Testing

### Integration Tests

Run the comprehensive integration test suite:

```bash
python test_integration.py
```

**Tests**:
- Package structure (42 modules)
- Main class imports
- Config and language file loading
- Translation manager
- Base classes
- Providers, processors, dialogs
- Utility functions

**Expected Output**:
```
======================================================================
SOTTO - REFACTORING INTEGRATION TESTS
======================================================================
[OK] tacet
[OK] tacet.engine
...
[PASS] All 42 modules imported successfully
...
10/10 tests passed
[SUCCESS] All integration tests passed! Refactoring successful!
```

### Manual Testing Checklist

**Application Startup**:
- [ ] Run `python main.py` - no import errors
- [ ] Main window appears
- [ ] System tray icon shows (if enabled)
- [ ] Microphone dropdown populated

**Dialogs**:
- [ ] Settings dialog opens (all tabs load)
- [ ] Voice Commands dialog opens
- [ ] Word Replacements dialog opens
- [ ] Templates dialog opens
- [ ] Session History dialog opens
- [ ] Statistics dialog opens
- [ ] About dialog opens
- [ ] Shortcuts dialog opens
- [ ] Export dialog opens

**Core Functionality**:
- [ ] Microphone selection works
- [ ] Start/Stop dictation button toggles
- [ ] Keyboard shortcuts work (Ctrl+S, Ctrl+O, etc.)
- [ ] Settings save and persist
- [ ] Language switching works

**Data Integrity**:
- [ ] config.json loads correctly
- [ ] languages.json loads correctly
- [ ] Settings changes persist after restart
- [ ] Session history saves/loads

### Unit Testing (Future)

Recommended structure:

```
tests/
├── conftest.py                    # Pytest fixtures
├── test_engine/
│   ├── test_audio.py              # Audio utilities
│   ├── test_processors.py         # Text processors
│   └── test_providers.py          # Transcription providers
├── test_gui/
│   ├── test_translation.py        # Translation manager
│   └── test_utils.py              # GUI utilities
└── test_integration/
    └── test_full_workflow.py      # End-to-end tests
```

**Running with pytest**:
```bash
pip install pytest pytest-cov
pytest tests/ -v
pytest tests/ --cov=tacet
```

---

## Design Patterns Used

### Patterns

1. **Singleton**: TranslationManager (single instance shared across GUI)
2. **Factory**: Provider selection based on config
3. **Observer**: Callback pattern for engine-to-GUI communication
4. **Template Method**: BaseDialog provides structure, subclasses fill in details
5. **Pipeline**: Text processors execute in sequence
6. **Strategy**: Different transcription providers (Local, OpenAI, Deepgram)

### Anti-Patterns Avoided

- **God Object**: Split monolithic files into focused modules
- **Circular Dependencies**: Strict import hierarchy
- **Magic Numbers**: Configuration file for all tunable parameters
- **Tight Coupling**: Callbacks and dependency injection
- **Global State**: Minimal (only TranslationManager singleton)

---

## Configuration

### Config File Structure

```json
{
  "engine": {
    "type": "local",              // Provider selection
    "language": "en"              // Transcription language
  },
  "local": { ... },               // Local provider settings
  "openai": { ... },              // OpenAI provider settings
  "deepgram": { ... },            // Deepgram provider settings
  "audio": {
    "sound_device": 0,            // Microphone device ID
    "sample_rate": 16000,
    "channels": 1
  },
  "voice_commands": { ... },      // Voice command processor
  "custom_replacements": { ... }, // Text replacement processor
  "templates": { ... },           // Template processor
  "gui": {
    "ui_language": "en",          // UI language
    "minimize_to_tray": true,
    "start_with_os": false
  }
}
```

### Language File Structure

```json
{
  "en": {
    "buttons": {
      "save": "Save",
      "cancel": "Cancel"
    },
    "main_window": {
      "title": "Tacet",
      "status_idle": "Idle",
      "status_listening": "Listening..."
    }
  },
  "es": { ... },
  "fr": { ... }
}
```

---

## Performance Considerations

### Memory Usage

- **Engine**: 1-10 GB (depends on model size)
- **GUI**: ~50-100 MB
- **Total**: Dominated by ML model

### Threading Model

- **Main Thread**: GUI event loop (CustomTkinter)
- **Background Thread**: Audio capture and transcription (DictationEngine)
- **Queue**: Thread-safe UI updates via `queue.Queue()`

### Optimization Tips

1. **Model Selection**: Use smaller models (tiny, base) for faster performance
2. **VAD Tuning**: Adjust `energy_threshold` to reduce false positives
3. **Silence Duration**: Lower `silence_ms` for faster finalization
4. **Compute Type**: Use `int8` or `int16` for faster inference (local mode)

---

## Future Enhancements

### Potential Extensions

1. **New Providers**:
   - Azure Speech Services
   - Google Cloud Speech-to-Text
   - Assembly AI

2. **New Processors**:
   - Grammar correction
   - Profanity filter
   - Language detection and translation

3. **New Dialogs**:
   - Advanced audio settings
   - Keyboard macro recorder
   - Plugin manager

4. **Features**:
   - Multiple simultaneous languages
   - Audio file transcription (drag and drop)
   - Real-time translation
   - Export to PDF, DOCX, etc.

---

## Troubleshooting Development Issues

### Import Errors

**Problem**: `ModuleNotFoundError: No module named 'tacet'`

**Solution**: Ensure you're in the project root directory where `tacet/` folder is located.

### Circular Imports

**Problem**: `ImportError: cannot import name 'X' from partially initialized module`

**Solution**: Check import hierarchy - lower levels shouldn't import from higher levels. Use singleton pattern for shared resources.

### Type Errors in IDE

**Problem**: IDE shows type errors for CustomTkinter widgets

**Solution**: Install type stubs: `pip install types-customtkinter` (if available) or add `# type: ignore` comments.

---

## Contributing Guidelines

### Code Style

- **PEP 8**: Follow Python style guide
- **Type Hints**: Use where helpful (function signatures)
- **Docstrings**: Module-level and class-level docstrings
- **Line Length**: Max 100 characters (flexible for readability)
- **File Size**: Keep files under 500 lines (split if larger)

### Adding Features

1. Plan the implementation (which modules affected?)
2. Follow existing patterns (providers, processors, dialogs)
3. Add to appropriate package level (respect import hierarchy)
4. Update `__init__.py` exports
5. Test integration (`python test_integration.py`)
6. Update documentation (README, ARCHITECTURE)

### Commit Messages

```
<type>: <subject>

<body>

Examples:
feat: Add Deepgram transcription provider
fix: Resolve circular import in translation manager
docs: Update architecture documentation
refactor: Split settings dialog into tabs
test: Add unit tests for text processors
```

---

## Conclusion

This architecture provides a solid foundation for a maintainable, extensible speech-to-text application. The modular structure makes it easy to add new features, fix bugs, and collaborate with other developers.

For questions or suggestions, please open an issue on GitHub.

**Happy coding!**
