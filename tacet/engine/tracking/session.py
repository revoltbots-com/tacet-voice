"""
Session History Manager

Manages session history - saving and loading previous transcription sessions.
"""

import json
import os
from datetime import datetime


class SessionHistoryManager:
    """
    Manages session history for transcription sessions.

    Features:
    - Auto-saves transcription sessions to JSON files
    - Load, view, restore, export, and delete sessions
    - Automatic cleanup when max_sessions limit reached
    """

    def __init__(self, config: dict, base_path: str):
        """
        Initialize SessionHistoryManager.

        Args:
            config: Configuration dictionary containing:
                - enabled: Whether session history is enabled
                - auto_save: Auto-save sessions
                - max_sessions: Maximum number of sessions to keep
                - save_path: Directory path for session files
            base_path: Base directory for the application
        """
        self.enabled = config.get("enabled", True)
        self.auto_save = config.get("auto_save", True)
        self.max_sessions = config.get("max_sessions", 50)
        self.save_path = os.path.join(base_path, config.get("save_path", "sessions"))

        # Ensure sessions directory exists
        if self.enabled:
            os.makedirs(self.save_path, exist_ok=True)

    def save_session(self, text: str, metadata: dict = None) -> str:
        """
        Save a transcription session.

        Args:
            text: Transcribed text
            metadata: Optional metadata dictionary

        Returns:
            Session file path, or None if save failed
        """
        if not self.enabled or not self.auto_save or not text.strip():
            return None

        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = f"session_{timestamp}.json"
        filepath = os.path.join(self.save_path, filename)

        session_data = {
            "timestamp": datetime.now().isoformat(),
            "text": text,
            "word_count": len(text.split()),
            "char_count": len(text),
            "metadata": metadata or {}
        }

        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(session_data, f, indent=2, ensure_ascii=False)

            # Cleanup old sessions if needed
            self._cleanup_old_sessions()

            return filepath
        except Exception as e:
            print(f"Warning: Could not save session: {e}")
            return None

    def load_sessions(self) -> list:
        """
        Load all saved sessions.

        Returns:
            List of session dictionaries (most recent first)
        """
        if not self.enabled or not os.path.exists(self.save_path):
            return []

        sessions = []
        try:
            for filename in sorted(os.listdir(self.save_path), reverse=True):
                if filename.endswith('.json'):
                    filepath = os.path.join(self.save_path, filename)
                    with open(filepath, 'r', encoding='utf-8') as f:
                        session = json.load(f)
                        session['filename'] = filename
                        sessions.append(session)
        except Exception as e:
            print(f"Warning: Could not load sessions: {e}")

        return sessions[:self.max_sessions]

    def _cleanup_old_sessions(self):
        """Remove sessions beyond max_sessions limit."""
        if not os.path.exists(self.save_path):
            return

        try:
            files = sorted(os.listdir(self.save_path))
            json_files = [f for f in files if f.endswith('.json')]

            while len(json_files) > self.max_sessions:
                oldest = json_files.pop(0)
                os.remove(os.path.join(self.save_path, oldest))
        except Exception as e:
            print(f"Warning: Could not cleanup sessions: {e}")

    def delete_session(self, filename: str) -> bool:
        """
        Delete a specific session.

        Args:
            filename: Session filename to delete

        Returns:
            True if successful, False otherwise
        """
        filepath = os.path.join(self.save_path, filename)
        try:
            if os.path.exists(filepath):
                os.remove(filepath)
                return True
        except Exception as e:
            print(f"Warning: Could not delete session: {e}")
        return False

    def clear_all(self) -> int:
        """
        Delete all saved sessions.

        Returns:
            Number of sessions deleted
        """
        if not os.path.exists(self.save_path):
            return 0

        count = 0
        try:
            for filename in os.listdir(self.save_path):
                if filename.endswith('.json'):
                    os.remove(os.path.join(self.save_path, filename))
                    count += 1
        except Exception as e:
            print(f"Warning: Could not clear all sessions: {e}")
        return count
