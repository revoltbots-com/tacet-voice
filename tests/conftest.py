"""Shared test fixtures for Tacet tests."""

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
