# Sotto — Publish-Ready Cleanup & Rebrand

## Overview

Prepare the project (currently named "Whisper Live Dictation") for its first public release on GitHub as **Sotto** — an open source speech-to-text dictation tool under the Revolt Bots brand. The codebase is feature-complete; this work is rebranding, cleanup, packaging, testing, and community setup.

**Strategy**: Open source (MIT) with GitHub Sponsors for donations. Future option to sell a packaged installer (Approach B) is kept open but not implemented now.

## 0. Rebrand: "Whisper Live Dictation" → "Sotto"

### Why "Sotto"?

The name comes from *sotto voce* — an Italian musical and theatrical term meaning "in a soft voice" or "under the breath." It captures the same spirit as "whisper" (quiet, unobtrusive speech) but through a more distinctive cultural reference.

Practical reasons for the rename:
- **"Whisper" is OpenAI's brand** — using it ties the project to a single upstream dependency and creates confusion about whether this is an official OpenAI product
- **Searchability** — "whisper dictation" returns OpenAI results; "Sotto" is unique in the tech/STT space
- **Identity** — Sotto is a product name, not a description of the underlying technology. The project supports multiple engines (local Whisper, OpenAI API, Deepgram), so naming it after one engine is misleading
- **Brevity** — 5 letters, easy to say, easy to type, memorable

### Rename scope

All references to "Whisper Live Dictation", "Whisper Dictation", and "whisper_dictation" need updating:

- **Package directory**: `whisper_dictation/` → `sotto/`
- **All `__init__.py` files**: update package references
- **All import statements**: `from whisper_dictation.` → `from sotto.`
- **Config files**: `config.json`, `config.example.json` — app name, title
- **Language files**: `languages.json` — all 5 languages' title and window references
- **README.md**, **ARCHITECTURE.md**, **CONTRIBUTING.md**, **GUI_README.md** — all doc references
- **Entry point**: `main.py` import
- **pyproject.toml**: package name `sotto`
- **GitHub repo name**: `revoltbots/sotto`
- **About dialog**: title, descriptions

Note: References to "Whisper" as the *transcription engine/model* (e.g., "uses OpenAI's Whisper model", "faster-whisper") remain unchanged — those refer to the upstream technology, not the product.

## 1. Remove Junk Files

Delete files that shouldn't be in the published repo:

- `temp_about.txt` — temporary About dialog code
- `temp_main_end.txt` — large temp file with main code snippet
- `nul` — Windows CMD redirect artifact

## 2. Remove Legacy v1.0 Files

These are the old monolithic files from before the v2.0 refactoring. All functionality has been migrated to the `sotto/` package:

- `stt_gui.py` (4,796 lines — old monolithic GUI)
- `stt_dictate.py` (314 lines — simple dictation script)
- `stt_live_dictate.py` (577 lines — legacy CLI)
- `dictation_engine.py` (1,421 lines — old monolithic engine)
- `translation_audit.py` (utility script, not part of the product)

## 3. Update LICENSE

Current: `Copyright (c) 2024` (no holder specified)
Updated: `Copyright (c) 2025-2026 Revolt Bots LLC`

License remains MIT — matches upstream dependencies (OpenAI Whisper, faster-whisper).

## 4. Create `pyproject.toml`

Modern Python packaging replacing the need for setup.py:

- Project metadata (name: `sotto`, version, description, author, URLs)
- Dependencies migrated from `requirements.txt`
- Entry point: `sotto = "sotto.main:main"` (or similar)
- Python version requirement (>=3.9)
- Optional dependency groups (e.g., `[gpu]` for ctranslate2)

`requirements.txt` is kept for users who prefer `pip install -r`.

## 5. Set Up Tests

Populate the existing `tests/` directory structure with pytest tests:

- `tests/test_engine/` — engine core, config loading, text processors
- `tests/test_gui/` — GUI component initialization (headless-safe where possible)
- `tests/test_integration/` — migrate/expand existing `test_integration.py`

Minimum coverage targets for launch:
- All providers instantiate correctly
- All processors transform text as expected
- Config loading and defaults work
- Translation manager loads languages
- Import integrity (all modules)

## 6. Add `.github/FUNDING.yml`

```yaml
github: [revoltbots]
```

This enables the "Sponsor" button on the GitHub repo page.

## 7. Create `.gitignore`

Exclude from version control:

- `__pycache__/`, `*.pyc`, `*.pyo`
- `.venv/`, `venv/`, `env/`
- `config.json` (user config — may contain API keys)
- `sessions/` (user session data)
- `stats.json` (user stats)
- `.idea/`, `.vscode/`
- `*.egg-info/`, `dist/`, `build/`
- `nul` (Windows artifact)

Keep tracked: `config.example.json` (template for users).

## 8. Rewrite README

Full rewrite for the new brand:

- Project name: **Sotto**
- Tagline explaining the name origin (sotto voce)
- Feature list, installation, usage, configuration
- GitHub Sponsors badge/link
- "RevoltBots.com" branding
- "Powered by" section acknowledging Whisper/faster-whisper as the underlying engine

## Out of Scope

- Git initialization (user will do this when ready to publish)
- Fine-tuned models (future consideration)
- Packaged installer / Electron/Tauri wrapper (future Approach B)
- Additional AI providers like Gemini (future feature)
- CI/CD pipeline (can be added after launch)

## Branding Notes

- Product name: **Sotto**
- Domain: RevoltBots.com (used in code/UI)
- Company: Revolt Bots LLC (used in legal/license context)
- GitHub: `revoltbots/sotto`
