"""
Usage Statistics Tracker

Tracks usage statistics for the dictation engine.
"""

import json
import os
from datetime import datetime


class UsageStatsTracker:
    """
    Track usage statistics for the dictation engine.

    Tracks words transcribed, sessions, time spent, and calculates time saved.
    """

    def __init__(self, stats_path: str):
        """
        Initialize UsageStatsTracker.

        Args:
            stats_path: Path to JSON file for storing statistics
        """
        self.stats_path = stats_path
        self.stats = self._load_stats()

        # Session tracking
        self.session_start = datetime.now()
        self.session_words = 0
        self.session_chars = 0

    def _load_stats(self) -> dict:
        """
        Load stats from JSON file.

        Returns:
            Statistics dictionary
        """
        if os.path.exists(self.stats_path):
            try:
                with open(self.stats_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except (OSError, json.JSONDecodeError, UnicodeDecodeError) as e:
                print(f"Warning: Could not load stats from {self.stats_path}: {e}")

        # Default stats structure
        return {
            "total_words": 0,
            "total_chars": 0,
            "total_sessions": 0,
            "total_time_seconds": 0,
            "sessions": []
        }

    def _save_stats(self):
        """Save stats to JSON file."""
        try:
            with open(self.stats_path, "w", encoding="utf-8") as f:
                json.dump(self.stats, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save stats: {e}")

    def record_text(self, text: str):
        """
        Record transcribed text.

        Args:
            text: Transcribed text to record
        """
        # Count words and characters
        words = len(text.split())
        chars = len(text)

        # Update session stats
        self.session_words += words
        self.session_chars += chars

        # Update total stats
        self.stats["total_words"] += words
        self.stats["total_chars"] += chars

    def end_session(self):
        """End current session and save stats."""
        session_duration = (datetime.now() - self.session_start).total_seconds()

        # Create session record
        session = {
            "date": self.session_start.isoformat(),
            "duration_seconds": round(session_duration, 1),
            "words": self.session_words,
            "chars": self.session_chars
        }

        # Add to sessions list (keep last 100)
        self.stats["sessions"].append(session)
        if len(self.stats["sessions"]) > 100:
            self.stats["sessions"] = self.stats["sessions"][-100:]

        # Update totals
        self.stats["total_sessions"] += 1
        self.stats["total_time_seconds"] += session_duration

        # Save stats
        self._save_stats()

    def get_stats(self) -> dict:
        """
        Get current statistics.

        Returns:
            Dictionary containing all statistics including time saved
        """
        # Calculate time saved (assuming 40 WPM typing speed)
        minutes_dictated = self.stats["total_time_seconds"] / 60
        minutes_typing = self.stats["total_words"] / 40  # 40 WPM average
        time_saved_minutes = max(0, minutes_typing - minutes_dictated)

        return {
            "total_words": self.stats["total_words"],
            "total_sessions": self.stats["total_sessions"],
            "total_time_seconds": self.stats["total_time_seconds"],
            "time_saved_minutes": round(time_saved_minutes, 1),
            "avg_words_per_session": round(self.stats["total_words"] / max(1, self.stats["total_sessions"]), 1),
            "sessions": self.stats["sessions"]
        }
