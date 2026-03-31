# Sotto — Rebrand & Publish-Ready Cleanup

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Rebrand "Whisper Live Dictation" to "Sotto", clean up the repo, add packaging and tests, and prepare for open source launch.

**Architecture:** The codebase is a modular Python package (`whisper_dictation/`) with engine and GUI layers. The rebrand renames the package to `sotto/`, updates all imports/strings, removes legacy files, adds modern packaging (`pyproject.toml`), and sets up pytest tests. No git is initialized — the user will init when ready to publish.

**Tech Stack:** Python 3.9+, CustomTkinter, faster-whisper, pytest

**Note:** Git is not initialized in this repo. Skip all `git commit` steps. Use test runs as verification checkpoints instead.

---

### Task 1: Delete Junk Files

**Files:**
- Delete: `temp_about.txt`
- Delete: `temp_main_end.txt`
- Delete: `nul`

- [ ] **Step 1: Delete temp and artifact files**

```bash
cd "d:/Projects/1 - Revolt Bot apps/Whisper"
rm -f temp_about.txt temp_main_end.txt nul
```

- [ ] **Step 2: Verify deletion**

```bash
ls temp_about.txt temp_main_end.txt nul 2>&1
```

Expected: All three files should report "No such file or directory"

---

### Task 2: Delete Legacy v1.0 Files

**Files:**
- Delete: `stt_gui.py`
- Delete: `stt_dictate.py`
- Delete: `stt_live_dictate.py`
- Delete: `dictation_engine.py`
- Delete: `translation_audit.py`
- Delete: `PHASE1_IMPLEMENTATION.md`
- Delete: `REFACTORING_SUMMARY.md`
- Delete: `ICON_INSTRUCTIONS.md`
- Delete: `GUI_README.md`

- [ ] **Step 1: Delete legacy source files**

```bash
cd "d:/Projects/1 - Revolt Bot apps/Whisper"
rm -f stt_gui.py stt_dictate.py stt_live_dictate.py dictation_engine.py translation_audit.py
```

- [ ] **Step 2: Delete internal-only documentation**

These docs reference the old monolithic structure and the refactoring process — not useful for open source contributors.

```bash
rm -f PHASE1_IMPLEMENTATION.md REFACTORING_SUMMARY.md ICON_INSTRUCTIONS.md GUI_README.md
```

- [ ] **Step 3: Verify deletion**

```bash
ls stt_gui.py stt_dictate.py stt_live_dictate.py dictation_engine.py translation_audit.py PHASE1_IMPLEMENTATION.md REFACTORING_SUMMARY.md ICON_INSTRUCTIONS.md GUI_README.md 2>&1
```

Expected: All files report "No such file or directory"

---

### Task 3: Rename Package Directory

**Files:**
- Rename: `whisper_dictation/` → `sotto/`

- [ ] **Step 1: Remove all `__pycache__` directories**

```bash
cd "d:/Projects/1 - Revolt Bot apps/Whisper"
find whisper_dictation -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null
```

- [ ] **Step 2: Rename the package directory**

```bash
mv whisper_dictation sotto
```

- [ ] **Step 3: Verify new structure**

```bash
find sotto -type f -name "*.py" | head -50
```

Expected: All `.py` files now under `sotto/` directory with same substructure (engine/, gui/, etc.)

---

### Task 4: Update All `__init__.py` Files

**Files:**
- Modify: `sotto/__init__.py`
- Modify: `sotto/engine/__init__.py`
- Modify: `sotto/gui/__init__.py`
- Modify: `sotto/engine/providers/__init__.py`
- Modify: `sotto/engine/processors/__init__.py`
- Modify: `sotto/engine/utils/__init__.py`
- Modify: `sotto/engine/tracking/__init__.py`
- Modify: `sotto/gui/core/__init__.py`
- Modify: `sotto/gui/dialogs/__init__.py`
- Modify: `sotto/gui/dialogs/components/__init__.py`
- Modify: `sotto/gui/utils/__init__.py`

- [ ] **Step 1: Update root `sotto/__init__.py`**

Replace the entire file with:

```python
"""
Sotto — Speech-to-text dictation, refined.

A professional, cross-platform speech-to-text dictation application.
The name comes from "sotto voce" — Italian for "in a soft voice."
"""

__version__ = "2.0.0"
__author__ = "Revolt Bots LLC"

# Main exports
from sotto.engine.dictation import DictationEngine
from sotto.gui.app import TranscriptionGUI

__all__ = [
    "DictationEngine",
    "TranscriptionGUI",
    "__version__",
    "__author__",
]
```

- [ ] **Step 2: Update `sotto/engine/__init__.py`**

Replace with:

```python
"""
Sotto Engine

Backend transcription engine with support for multiple providers.
"""

from sotto.engine.dictation import DictationEngine

__all__ = ["DictationEngine"]
```

- [ ] **Step 3: Update `sotto/gui/__init__.py`**

Replace with:

```python
"""
Sotto GUI

Modern CustomTkinter-based graphical interface.
"""

from sotto.gui.app import TranscriptionGUI, main

__all__ = ["TranscriptionGUI", "main"]
```

- [ ] **Step 4: Bulk-update all remaining `__init__.py` files**

All other `__init__.py` files use `from whisper_dictation.` imports. Replace them all:

```bash
cd "d:/Projects/1 - Revolt Bot apps/Whisper"
find sotto -name "__init__.py" -exec sed -i 's/from whisper_dictation\./from sotto./g' {} +
find sotto -name "__init__.py" -exec sed -i 's/import whisper_dictation/import sotto/g' {} +
```

- [ ] **Step 5: Update docstrings in remaining `__init__.py` files**

```bash
find sotto -name "__init__.py" -exec sed -i 's/Whisper Dictation/Sotto/g' {} +
find sotto -name "__init__.py" -exec sed -i 's/Whisper dictation/Sotto/g' {} +
```

- [ ] **Step 6: Verify no `whisper_dictation` references remain in `__init__.py` files**

```bash
grep -r "whisper_dictation" sotto --include="__init__.py"
```

Expected: No output (no matches)

---

### Task 5: Update All Internal Imports

**Files:**
- Modify: All `.py` files under `sotto/` (excluding `__init__.py` — already done)

- [ ] **Step 1: Bulk-replace import statements in all `.py` files**

```bash
cd "d:/Projects/1 - Revolt Bot apps/Whisper"
find sotto -name "*.py" ! -name "__init__.py" -exec sed -i 's/from whisper_dictation\./from sotto./g' {} +
find sotto -name "*.py" ! -name "__init__.py" -exec sed -i 's/import whisper_dictation/import sotto/g' {} +
```

- [ ] **Step 2: Verify no `whisper_dictation` references remain in source**

```bash
grep -r "whisper_dictation" sotto/
```

Expected: No output (no matches)

- [ ] **Step 3: Verify Python can import the package**

```bash
cd "d:/Projects/1 - Revolt Bot apps/Whisper"
python -c "from sotto import __version__; print(f'Sotto v{__version__}')"
```

Expected: `Sotto v2.0.0`

---

### Task 6: Update Entry Point

**Files:**
- Modify: `main.py`

- [ ] **Step 1: Rewrite `main.py`**

Replace the entire file with:

```python
"""
Sotto — Speech-to-text dictation, refined.

Professional voice dictation application with real-time transcription,
voice commands, and intelligent text processing.

The name comes from "sotto voce" — Italian for "in a soft voice."
"""

from sotto.gui.app import main

if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Verify entry point works**

```bash
python -c "import main" 2>&1 | head -5
```

Expected: No import errors (GUI may fail to launch in headless mode, but import should succeed or fail on GUI dependencies, not on missing modules)

---

### Task 7: Update Config Files

**Files:**
- Modify: `config.json`
- Modify: `config.example.json`

- [ ] **Step 1: Update `config.json` app section**

Change the `"app"` block:
```json
{
  "app": {
    "name": "Sotto",
    "version": "2.0.0",
    "author": "RevoltBots.com",
    "website": "https://revoltbots.com",
    "github": "https://github.com/revoltbots/sotto"
  },
```

- [ ] **Step 2: Update `config.example.json` app section**

Same changes:
```json
{
  "app": {
    "name": "Sotto",
    "version": "2.0.0",
    "author": "RevoltBots.com",
    "website": "https://revoltbots.com",
    "github": "https://github.com/revoltbots/sotto"
  },
```

- [ ] **Step 3: Verify JSON is valid**

```bash
python -c "import json; json.load(open('config.json')); print('config.json OK')"
python -c "import json; json.load(open('config.example.json')); print('config.example.json OK')"
```

Expected: Both print "OK"

---

### Task 8: Update `languages.json`

**Files:**
- Modify: `languages.json`

- [ ] **Step 1: Update all product name references across all 5 languages**

The file contains title strings like `"Whisper Dictation - by RevoltBots.com"` in English, Spanish, French, German, and Japanese. Update all of them:

```bash
cd "d:/Projects/1 - Revolt Bot apps/Whisper"
sed -i 's/"Whisper Dictation - by RevoltBots.com"/"Sotto - by RevoltBots.com"/g' languages.json
sed -i 's/"Whisper Dictado - por RevoltBots.com"/"Sotto - por RevoltBots.com"/g' languages.json
sed -i 's/"Dictée Whisper - par RevoltBots.com"/"Sotto - par RevoltBots.com"/g' languages.json
sed -i 's/"Whisper Diktat - von RevoltBots.com"/"Sotto - von RevoltBots.com"/g' languages.json
```

- [ ] **Step 2: Update the app name field in languages.json**

```bash
sed -i 's/"name": "Whisper Live Dictation"/"name": "Sotto"/g' languages.json
sed -i 's/"author": "RevoltBots.com"/"author": "RevoltBots.com"/g' languages.json
```

Note: Also check for any Japanese translation title that references Whisper and update it.

- [ ] **Step 3: Search for any remaining "Whisper" product references**

```bash
grep -n "Whisper" languages.json | grep -v "faster-whisper" | grep -v "OpenAI" | grep -v "whisper-1"
```

Review output: Any remaining "Whisper" references that are product names (not engine/model references) should be updated to "Sotto". Engine references like "whisper-1" (OpenAI model name) stay as-is.

- [ ] **Step 4: Verify JSON is valid**

```bash
python -c "import json; data=json.load(open('languages.json', encoding='utf-8')); print(f'languages.json OK - {len(data)} keys')"
```

Expected: Prints OK with key count

---

### Task 9: Update LICENSE

**Files:**
- Modify: `LICENSE`

- [ ] **Step 1: Update copyright line**

Change line 3 from:
```
Copyright (c) 2024
```
to:
```
Copyright (c) 2025-2026 Revolt Bots LLC
```

---

### Task 10: Create `pyproject.toml`

**Files:**
- Create: `pyproject.toml`

- [ ] **Step 1: Create `pyproject.toml`**

```toml
[build-system]
requires = ["setuptools>=68.0", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "sotto"
version = "2.0.0"
description = "Speech-to-text dictation, refined. Real-time voice transcription with intelligent text processing."
readme = "README.md"
license = {text = "MIT"}
requires-python = ">=3.9"
authors = [
    {name = "Revolt Bots LLC", email = "hello@revoltbots.com"},
]
keywords = ["speech-to-text", "dictation", "whisper", "transcription", "voice"]
dependencies = [
    "numpy>=1.24.0",
    "sounddevice>=0.4.6",
    "soundfile>=0.12.1",
    "faster-whisper>=0.10.0",
    "pynput>=1.7.6",
    "requests>=2.31.0",
    "customtkinter>=5.2.0",
    "pyperclip>=1.8.0",
    "pystray>=0.19.0",
    "Pillow>=9.0.0",
    "pywin32>=305; sys_platform == 'win32'",
    "winshell>=0.6; sys_platform == 'win32'",
]
classifiers = [
    "Development Status :: 4 - Beta",
    "Intended Audience :: End Users/Desktop",
    "License :: OSI Approved :: MIT License",
    "Operating System :: OS Independent",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.9",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
    "Topic :: Multimedia :: Sound/Audio :: Speech",
]

[project.urls]
Homepage = "https://revoltbots.com"
Repository = "https://github.com/revoltbots/sotto"
Issues = "https://github.com/revoltbots/sotto/issues"

[project.scripts]
sotto = "sotto.gui.app:main"

[project.optional-dependencies]
gpu = ["ctranslate2>=3.20.0"]

[tool.setuptools.packages.find]
include = ["sotto*"]

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
```

- [ ] **Step 2: Verify pyproject.toml parses correctly**

```bash
python -c "
import tomllib
with open('pyproject.toml', 'rb') as f:
    data = tomllib.load(f)
print(f'Project: {data[\"project\"][\"name\"]} v{data[\"project\"][\"version\"]}')
"
```

Expected: `Project: sotto v2.0.0`

---

### Task 11: Update `.gitignore`

**Files:**
- Modify: `.gitignore`

- [ ] **Step 1: Update `.gitignore`**

The existing `.gitignore` has a section that ignores test files:
```
# Test files
test_*.py
*_test.py
```

Remove that section — we want tests tracked. Also add `sessions/` and `stats.json`:

Replace the entire file with:

```gitignore
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual environments
venv/
env/
ENV/
.venv/

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# Model cache (Hugging Face)
.cache/
models/

# User config (may contain API keys)
config.json

# User data
sessions/
stats.json

# Temporary audio files
*.wav
temp/
tmp/

# Environment variables
.env
.env.local

# Logs
*.log

# OS
Thumbs.db
.DS_Store

# Claude Code
.claude/
```

---

### Task 12: Create `.github/FUNDING.yml`

**Files:**
- Create: `.github/FUNDING.yml`

- [ ] **Step 1: Create `.github` directory and funding file**

```bash
mkdir -p "d:/Projects/1 - Revolt Bot apps/Whisper/.github"
```

- [ ] **Step 2: Create `FUNDING.yml`**

```yaml
github: [revoltbots]
```

---

### Task 13: Update `test_integration.py`

**Files:**
- Modify: `test_integration.py`

- [ ] **Step 1: Update all imports from `whisper_dictation` to `sotto`**

```bash
cd "d:/Projects/1 - Revolt Bot apps/Whisper"
sed -i 's/from whisper_dictation/from sotto/g' test_integration.py
sed -i 's/import whisper_dictation/import sotto/g' test_integration.py
sed -i 's/whisper_dictation\./sotto./g' test_integration.py
```

- [ ] **Step 2: Update docstrings and string references**

```bash
sed -i 's/Whisper Live Dictation/Sotto/g' test_integration.py
sed -i 's/Whisper Dictation/Sotto/g' test_integration.py
sed -i 's/whisper_dictation/sotto/g' test_integration.py
```

- [ ] **Step 3: Run the integration tests**

```bash
cd "d:/Projects/1 - Revolt Bot apps/Whisper"
python test_integration.py
```

Expected: All tests pass (10/10 or similar). If any fail, fix the specific import that's broken.

---

### Task 14: Write Unit Tests

**Files:**
- Create: `tests/conftest.py`
- Create: `tests/test_engine/test_config.py`
- Create: `tests/test_engine/test_processors.py`
- Create: `tests/test_engine/test_providers.py`
- Create: `tests/test_engine/test_text_utils.py`
- Create: `tests/test_integration/test_imports.py`

- [ ] **Step 1: Create `tests/conftest.py`**

```python
"""Shared test fixtures for Sotto tests."""

import json
import os
import pytest


@pytest.fixture
def sample_config():
    """Load the example config for testing."""
    config_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        "config.example.json"
    )
    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture
def languages_data():
    """Load the languages file for testing."""
    lang_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        "languages.json"
    )
    with open(lang_path, "r", encoding="utf-8") as f:
        return json.load(f)
```

- [ ] **Step 2: Create `tests/test_engine/test_config.py`**

```python
"""Tests for configuration loading and validation."""

import json
import os
import pytest


class TestConfigLoading:
    """Test that config files load and contain required fields."""

    def test_example_config_is_valid_json(self):
        config_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            "config.example.json"
        )
        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)
        assert isinstance(config, dict)

    def test_example_config_has_app_section(self, sample_config):
        assert "app" in sample_config
        assert sample_config["app"]["name"] == "Sotto"
        assert "author" in sample_config["app"]
        assert "website" in sample_config["app"]

    def test_example_config_has_engine_setting(self, sample_config):
        assert "engine" in sample_config
        assert sample_config["engine"] in ("local", "openai", "deepgram")

    def test_example_config_has_audio_section(self, sample_config):
        assert "audio" in sample_config
        assert "sample_rate" in sample_config["audio"]

    def test_example_config_has_hotkey(self, sample_config):
        assert "hotkey" in sample_config
        assert isinstance(sample_config["hotkey"], str)


class TestLanguagesFile:
    """Test that the languages file is valid and complete."""

    def test_languages_file_is_valid_json(self, languages_data):
        assert isinstance(languages_data, dict)

    def test_languages_has_app_section(self, languages_data):
        assert "app" in languages_data

    def test_languages_has_translations(self, languages_data):
        assert "languages" in languages_data
        langs = languages_data["languages"]
        assert isinstance(langs, dict)
        assert len(langs) >= 1

    def test_branding_is_sotto(self, languages_data):
        app = languages_data.get("app", {})
        if "name" in app:
            assert "Sotto" in app["name"]
```

- [ ] **Step 3: Create `tests/test_engine/test_processors.py`**

```python
"""Tests for text processors."""

import pytest


class TestVoiceCommandProcessor:
    """Test voice command processing."""

    def test_import(self):
        from sotto.engine.processors import VoiceCommandProcessor
        assert VoiceCommandProcessor is not None


class TestTextReplacementProcessor:
    """Test text replacement processing."""

    def test_import(self):
        from sotto.engine.processors import TextReplacementProcessor
        assert TextReplacementProcessor is not None


class TestAutoPunctuationProcessor:
    """Test auto-punctuation processing."""

    def test_import(self):
        from sotto.engine.processors import AutoPunctuationProcessor
        assert AutoPunctuationProcessor is not None


class TestTimestampProcessor:
    """Test timestamp processing."""

    def test_import(self):
        from sotto.engine.processors import TimestampProcessor
        assert TimestampProcessor is not None


class TestTemplateProcessor:
    """Test template processing."""

    def test_import(self):
        from sotto.engine.processors import TemplateProcessor
        assert TemplateProcessor is not None
```

- [ ] **Step 4: Create `tests/test_engine/test_providers.py`**

```python
"""Tests for transcription providers."""

import pytest


class TestLocalEngine:
    """Test local (faster-whisper) provider."""

    def test_import(self):
        from sotto.engine.providers import LocalEngine
        assert LocalEngine is not None


class TestOpenAIEngine:
    """Test OpenAI API provider."""

    def test_import(self):
        from sotto.engine.providers import OpenAIEngine
        assert OpenAIEngine is not None


class TestDeepgramEngine:
    """Test Deepgram API provider."""

    def test_import(self):
        from sotto.engine.providers import DeepgramEngine
        assert DeepgramEngine is not None


class TestBaseEngine:
    """Test base engine abstract class."""

    def test_import(self):
        from sotto.engine.base import BaseEngine
        assert BaseEngine is not None
```

- [ ] **Step 5: Create `tests/test_engine/test_text_utils.py`**

```python
"""Tests for text utility functions."""

import pytest


class TestTextUtils:
    """Test text utility imports and availability."""

    def test_import_text_module(self):
        from sotto.engine.utils import text
        assert text is not None

    def test_import_audio_module(self):
        from sotto.engine.utils import audio
        assert audio is not None

    def test_import_keyboard_module(self):
        from sotto.engine.utils import keyboard
        assert keyboard is not None
```

- [ ] **Step 6: Create `tests/test_integration/test_imports.py`**

Migrate the core import verification from `test_integration.py` into pytest format:

```python
"""Integration tests — verify all package modules can be imported."""

import pytest


class TestPackageImports:
    """Verify all sotto package modules import successfully."""

    def test_import_root(self):
        import sotto
        assert sotto.__version__ == "2.0.0"

    def test_import_main_classes(self):
        from sotto import DictationEngine, TranscriptionGUI
        assert DictationEngine is not None
        assert TranscriptionGUI is not None

    def test_import_engine(self):
        from sotto.engine import DictationEngine
        assert DictationEngine is not None

    def test_import_engine_base(self):
        from sotto.engine.base import BaseEngine
        assert BaseEngine is not None

    def test_import_providers(self):
        from sotto.engine.providers import LocalEngine, OpenAIEngine, DeepgramEngine
        assert LocalEngine is not None
        assert OpenAIEngine is not None
        assert DeepgramEngine is not None

    def test_import_processors(self):
        from sotto.engine.processors import (
            VoiceCommandProcessor,
            TextReplacementProcessor,
            AutoPunctuationProcessor,
            TimestampProcessor,
            TemplateProcessor,
        )
        assert VoiceCommandProcessor is not None

    def test_import_engine_utils(self):
        from sotto.engine.utils import audio, keyboard, text
        assert audio is not None

    def test_import_tracking(self):
        from sotto.engine.tracking import session, stats
        assert session is not None

    def test_import_gui(self):
        from sotto.gui import TranscriptionGUI
        assert TranscriptionGUI is not None

    def test_import_gui_core(self):
        from sotto.gui.core.translation import get_translator
        assert get_translator is not None

    def test_import_gui_dialogs(self):
        from sotto.gui.dialogs import (
            SettingsDialog,
            VoiceCommandsDialog,
            WordReplacementsDialog,
            TemplatesDialog,
            SessionHistoryDialog,
            StatisticsDialog,
            AboutDialog,
            ShortcutsDialog,
            ExportDialog,
        )
        assert SettingsDialog is not None

    def test_import_gui_dialog_components(self):
        from sotto.gui.dialogs.components import EditorList, ItemRow, TextEditor
        assert EditorList is not None

    def test_import_gui_utils(self):
        from sotto.gui.utils import IS_MAC, IS_WINDOWS, normalize_shortcut
        assert isinstance(IS_MAC, bool)
        assert isinstance(IS_WINDOWS, bool)
```

- [ ] **Step 7: Run all pytest tests**

```bash
cd "d:/Projects/1 - Revolt Bot apps/Whisper"
python -m pytest tests/ -v
```

Expected: All tests pass. If any imports fail, fix the broken import in the corresponding `sotto/` source file.

---

### Task 15: Rewrite README

**Files:**
- Modify: `README.md`

- [ ] **Step 1: Rewrite `README.md`**

Replace the entire file. The README should contain these sections in order:

1. **Title & badges**: `# Sotto` with a one-line tagline and GitHub Sponsors badge
2. **What is Sotto?**: 2-3 sentence description explaining the name (sotto voce) and what it does
3. **Features**: Bullet list of key features (real-time transcription, multiple engines, voice commands, templates, word replacements, timestamps, session history, multi-language UI, system tray, cross-platform)
4. **Quick Start**: Installation steps (`git clone`, `pip install -r requirements.txt`, `python main.py`)
5. **Transcription Engines**: Table showing Local (faster-whisper), OpenAI API, Deepgram API with pros/cons
6. **Configuration**: Brief explanation of `config.example.json` → `config.json`, key settings
7. **Voice Commands**: Brief explanation with examples
8. **Keyboard Shortcuts**: Default hotkey and how to change it
9. **Supported Languages**: List the 5 UI languages
10. **Contributing**: Link to CONTRIBUTING.md
11. **License**: MIT — Revolt Bots LLC
12. **Acknowledgments**: Credit faster-whisper, OpenAI Whisper model, CustomTkinter

Important: Keep "Whisper" only when referring to the upstream OpenAI model or faster-whisper library. The product is always "Sotto".

Include this sponsor badge near the top:
```markdown
[![Sponsor](https://img.shields.io/badge/Sponsor-❤-ea4aaa)](https://github.com/sponsors/revoltbots)
```

- [ ] **Step 2: Verify no broken references**

```bash
grep -n "Whisper Live Dictation\|whisper_dictation\|whisper-live-dictation" README.md
```

Expected: No matches (all product references should be "Sotto" now)

---

### Task 16: Update Remaining Documentation

**Files:**
- Modify: `ARCHITECTURE.md`
- Modify: `CONTRIBUTING.md`

- [ ] **Step 1: Update `ARCHITECTURE.md`**

Replace all product name references:

```bash
cd "d:/Projects/1 - Revolt Bot apps/Whisper"
sed -i 's/Whisper Live Dictation/Sotto/g' ARCHITECTURE.md
sed -i 's/Whisper Dictation/Sotto/g' ARCHITECTURE.md
sed -i 's/whisper_dictation/sotto/g' ARCHITECTURE.md
sed -i 's/whisper-live-dictation/sotto/g' ARCHITECTURE.md
```

Then manually review to ensure "Whisper" references to the engine/model are preserved (e.g., "uses OpenAI's Whisper model", "faster-whisper").

- [ ] **Step 2: Update `CONTRIBUTING.md`**

```bash
sed -i 's/Whisper Live Dictation/Sotto/g' CONTRIBUTING.md
sed -i 's/whisper-live-dictation/sotto/g' CONTRIBUTING.md
sed -i 's/whisper_dictation/sotto/g' CONTRIBUTING.md
```

- [ ] **Step 3: Verify no stale product name references in docs**

```bash
grep -rn "Whisper Live Dictation\|whisper_dictation\|whisper-live-dictation" *.md
```

Expected: No matches. Any remaining "Whisper" should only be engine/model references.

---

### Task 17: Update About Dialog Defaults

**Files:**
- Modify: `sotto/gui/dialogs/about.py`

- [ ] **Step 1: Update fallback strings in about dialog**

The about dialog has hardcoded fallback values. Update them:

Find:
```python
author = app_info.get("author", "RevoltBots.com")
website = app_info.get("website", "https://revoltbots.com")
github = app_info.get("github", "https://github.com/revoltbots/whisper-live-dictation")
```

Replace with:
```python
author = app_info.get("author", "RevoltBots.com")
website = app_info.get("website", "https://revoltbots.com")
github = app_info.get("github", "https://github.com/revoltbots/sotto")
```

---

### Task 18: Update Autostart References

**Files:**
- Modify: `sotto/gui/utils/autostart.py`

- [ ] **Step 1: Check for product name references in autostart**

```bash
grep -n "Whisper\|whisper" sotto/gui/utils/autostart.py
```

If there are references to "Whisper Dictation" or "WhisperDictation" as the app name for Windows registry/startup entries, update them to "Sotto".

- [ ] **Step 2: Update any found references**

Replace product name references (e.g., startup entry names, registry keys) from "Whisper Dictation" / "WhisperDictation" to "Sotto". Keep references to the Whisper engine/model unchanged.

---

### Task 19: Final Verification

- [ ] **Step 1: Run integration tests**

```bash
cd "d:/Projects/1 - Revolt Bot apps/Whisper"
python test_integration.py
```

Expected: All tests pass

- [ ] **Step 2: Run pytest suite**

```bash
python -m pytest tests/ -v
```

Expected: All tests pass

- [ ] **Step 3: Verify package imports**

```bash
python -c "
from sotto import DictationEngine, TranscriptionGUI, __version__, __author__
print(f'Sotto v{__version__} by {__author__}')
print('All imports OK')
"
```

Expected:
```
Sotto v2.0.0 by Revolt Bots LLC
All imports OK
```

- [ ] **Step 4: Scan for any remaining `whisper_dictation` references**

```bash
grep -r "whisper_dictation" --include="*.py" --include="*.json" --include="*.md" --include="*.toml" --include="*.yml" . | grep -v ".venv" | grep -v "__pycache__" | grep -v "docs/superpowers"
```

Expected: No matches (the spec files in docs/superpowers may reference the old name for historical context — that's fine)

- [ ] **Step 5: Scan for stale product name references**

```bash
grep -r "Whisper Live Dictation\|Whisper Dictation" --include="*.py" --include="*.json" --include="*.md" --include="*.toml" . | grep -v ".venv" | grep -v "__pycache__" | grep -v "docs/superpowers"
```

Expected: No matches

- [ ] **Step 6: Verify file structure is clean**

```bash
ls -la *.py *.json *.md *.txt *.toml .gitignore LICENSE 2>/dev/null
```

Expected files present:
- `main.py`
- `config.json`, `config.example.json`, `languages.json`
- `README.md`, `ARCHITECTURE.md`, `CONTRIBUTING.md`
- `requirements.txt`
- `pyproject.toml`
- `.gitignore`
- `LICENSE`

Expected files absent:
- `temp_about.txt`, `temp_main_end.txt`, `nul`
- `stt_gui.py`, `stt_dictate.py`, `stt_live_dictate.py`, `dictation_engine.py`
- `translation_audit.py`, `GUI_README.md`, `PHASE1_IMPLEMENTATION.md`, `REFACTORING_SUMMARY.md`, `ICON_INSTRUCTIONS.md`
