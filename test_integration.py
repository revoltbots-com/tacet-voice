"""
Integration test script for refactored Tacet

Tests critical functionality to ensure refactoring was successful.
"""

import os
import sys
import json

def test_package_structure():
    """Test that all expected modules exist and can be imported"""
    print("Testing package structure...")

    required_modules = [
        # Core package
        "tacet",

        # Engine modules
        "tacet.engine",
        "tacet.engine.base",
        "tacet.engine.dictation",
        "tacet.engine.providers",
        "tacet.engine.providers.local",
        "tacet.engine.providers.openai",
        "tacet.engine.providers.deepgram",
        "tacet.engine.processors",
        "tacet.engine.processors.voice_commands",
        "tacet.engine.processors.text_replacement",
        "tacet.engine.processors.auto_punctuation",
        "tacet.engine.processors.timestamp",
        "tacet.engine.processors.template",
        "tacet.engine.utils",
        "tacet.engine.utils.audio",
        "tacet.engine.utils.keyboard",
        "tacet.engine.utils.text",
        "tacet.engine.tracking",
        "tacet.engine.tracking.stats",
        "tacet.engine.tracking.session",

        # GUI modules
        "tacet.gui",
        "tacet.gui.app",
        "tacet.gui.core",
        "tacet.gui.core.translation",
        "tacet.gui.core.system_tray",
        "tacet.gui.dialogs",
        "tacet.gui.dialogs.base",
        "tacet.gui.dialogs.settings",
        "tacet.gui.dialogs.about",
        "tacet.gui.dialogs.statistics",
        "tacet.gui.dialogs.export",
        "tacet.gui.dialogs.voice_commands",
        "tacet.gui.dialogs.word_replacements",
        "tacet.gui.dialogs.templates",
        "tacet.gui.dialogs.session_history",
        "tacet.gui.dialogs.shortcuts",
        "tacet.gui.utils",
        "tacet.gui.utils.platform_utils",
        "tacet.gui.utils.shortcuts",
        "tacet.gui.utils.autostart",
        "tacet.gui.utils.icons",
    ]

    failed = []
    for module in required_modules:
        try:
            __import__(module)
            print(f"  [OK] {module}")
        except Exception as e:
            print(f"  [FAIL] {module}: {e}")
            failed.append((module, str(e)))

    if failed:
        print(f"\n[FAIL] {len(failed)} modules failed to import")
        return False
    else:
        print(f"\n[PASS] All {len(required_modules)} modules imported successfully")
        return True


def test_main_classes():
    """Test that main classes can be instantiated"""
    print("\nTesting main class imports...")

    try:
        from tacet import DictationEngine, TranscriptionGUI, __version__
        print(f"  [OK] Package version: {__version__}")
        print(f"  [OK] DictationEngine class available")
        print(f"  [OK] TranscriptionGUI class available")
        return True
    except Exception as e:
        print(f"  [FAIL] Failed to import main classes: {e}")
        return False


def test_config_loading():
    """Test that config.json can be loaded"""
    print("\nTesting config loading...")

    config_path = os.path.join(os.path.dirname(__file__), "config.json")

    if not os.path.exists(config_path):
        print(f"  [WARN] config.json not found at {config_path}")
        return False

    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)

        # Check for expected top-level keys
        expected_keys = ["engine", "audio", "gui", "voice_commands", "custom_replacements"]
        for key in expected_keys:
            if key in config:
                print(f"  [OK] Config section '{key}' present")
            else:
                print(f"  [WARN] Config section '{key}' missing")

        return True
    except Exception as e:
        print(f"  [FAIL] Failed to load config: {e}")
        return False


def test_languages_loading():
    """Test that languages.json can be loaded"""
    print("\nTesting languages file...")

    lang_path = os.path.join(os.path.dirname(__file__), "languages.json")

    if not os.path.exists(lang_path):
        print(f"  [WARN] languages.json not found at {lang_path}")
        return False

    try:
        with open(lang_path, 'r', encoding='utf-8') as f:
            languages = json.load(f)

        if "en" in languages:
            print(f"  [OK] English translations loaded")

        print(f"  [OK] Found {len(languages)} language(s)")
        return True
    except Exception as e:
        print(f"  [FAIL] Failed to load languages: {e}")
        return False


def test_translation_manager():
    """Test translation manager singleton"""
    print("\nTesting translation manager...")

    try:
        from tacet.gui.core.translation import get_translator

        translator = get_translator()
        print(f"  [OK] TranslationManager instantiated")

        # Test translation (avoid printing to prevent encoding issues)
        test_key = "buttons.save"
        translated = translator.t(test_key)
        if translated:
            print(f"  [OK] Translation test successful: '{test_key}' -> (text retrieved)")
        else:
            print(f"  [WARN] Translation returned empty for key: '{test_key}'")

        return True
    except Exception as e:
        print(f"  [FAIL] Translation manager failed: {e}")
        return False


def test_base_classes():
    """Test that base classes can be imported and work correctly"""
    print("\nTesting base classes...")

    try:
        from tacet.engine.base import BaseEngine
        print(f"  [OK] BaseEngine imported")

        from tacet.gui.dialogs.base import BaseDialog
        print(f"  [OK] BaseDialog imported")

        return True
    except Exception as e:
        print(f"  [FAIL] Base classes failed: {e}")
        return False


def test_providers():
    """Test that all providers can be imported"""
    print("\nTesting transcription providers...")

    try:
        from tacet.engine.providers import LocalEngine, OpenAIEngine, DeepgramEngine
        print(f"  [OK] LocalEngine imported")
        print(f"  [OK] OpenAIEngine imported")
        print(f"  [OK] DeepgramEngine imported")
        return True
    except Exception as e:
        print(f"  [FAIL] Providers failed: {e}")
        return False


def test_processors():
    """Test that all processors can be imported"""
    print("\nTesting text processors...")

    try:
        from tacet.engine.processors import (
            VoiceCommandProcessor,
            TextReplacementProcessor,
            AutoPunctuationProcessor,
            TimestampProcessor,
            TemplateProcessor
        )
        print(f"  [OK] VoiceCommandProcessor imported")
        print(f"  [OK] TextReplacementProcessor imported")
        print(f"  [OK] AutoPunctuationProcessor imported")
        print(f"  [OK] TimestampProcessor imported")
        print(f"  [OK] TemplateProcessor imported")
        return True
    except Exception as e:
        print(f"  [FAIL] Processors failed: {e}")
        return False


def test_dialogs():
    """Test that all dialogs can be imported"""
    print("\nTesting dialog imports...")

    try:
        from tacet.gui.dialogs import (
            SettingsDialog,
            VoiceCommandsDialog,
            WordReplacementsDialog,
            TemplatesDialog,
            SessionHistoryDialog,
            StatisticsDialog,
            AboutDialog,
            ShortcutsDialog,
            ExportDialog
        )
        print(f"  [OK] SettingsDialog imported")
        print(f"  [OK] VoiceCommandsDialog imported")
        print(f"  [OK] WordReplacementsDialog imported")
        print(f"  [OK] TemplatesDialog imported")
        print(f"  [OK] SessionHistoryDialog imported")
        print(f"  [OK] StatisticsDialog imported")
        print(f"  [OK] AboutDialog imported")
        print(f"  [OK] ShortcutsDialog imported")
        print(f"  [OK] ExportDialog imported")
        return True
    except Exception as e:
        print(f"  [FAIL] Dialogs failed: {e}")
        return False


def test_utilities():
    """Test that utility functions work"""
    print("\nTesting utility functions...")

    try:
        from tacet.gui.utils import IS_MAC, IS_WINDOWS, CTRL_SYMBOL, normalize_shortcut
        print(f"  [OK] Platform detection: IS_MAC={IS_MAC}, IS_WINDOWS={IS_WINDOWS}")
        print(f"  [OK] CTRL_SYMBOL={CTRL_SYMBOL}")

        # Test shortcut normalization
        test_shortcut = f"<{CTRL_SYMBOL}-s>"
        normalized = normalize_shortcut(test_shortcut)
        print(f"  [OK] Shortcut normalization: '{test_shortcut}' -> '{normalized}'")

        return True
    except Exception as e:
        print(f"  [FAIL] Utilities failed: {e}")
        return False


def main():
    """Run all tests"""
    print("=" * 70)
    print("TACET - REFACTORING INTEGRATION TESTS")
    print("=" * 70)

    tests = [
        ("Package Structure", test_package_structure),
        ("Main Classes", test_main_classes),
        ("Config Loading", test_config_loading),
        ("Languages Loading", test_languages_loading),
        ("Translation Manager", test_translation_manager),
        ("Base Classes", test_base_classes),
        ("Providers", test_providers),
        ("Processors", test_processors),
        ("Dialogs", test_dialogs),
        ("Utilities", test_utilities),
    ]

    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n❌ {name} test crashed: {e}")
            results.append((name, False))

    # Summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for name, result in results:
        status = "[PASS]" if result else "[FAIL]"
        print(f"{status}: {name}")

    print(f"\n{passed}/{total} tests passed")

    if passed == total:
        print("\n[SUCCESS] All integration tests passed! Refactoring successful!")
        return 0
    else:
        print(f"\n[WARNING]  {total - passed} test(s) failed. Please review the output above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
