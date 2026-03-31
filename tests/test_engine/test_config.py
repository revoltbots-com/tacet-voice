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
        assert sample_config["app"]["name"] == "Tacet"
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

    def test_languages_has_info_section(self, languages_data):
        assert "_info" in languages_data

    def test_languages_has_english(self, languages_data):
        assert "en" in languages_data
        en = languages_data["en"]
        assert isinstance(en, dict)
        assert len(en) >= 1

    def test_branding_is_tacet(self, languages_data):
        # Check that Tacet branding appears somewhere in the info or English content
        info = languages_data.get("_info", {})
        description = info.get("description", "")
        assert "Tacet" in description
