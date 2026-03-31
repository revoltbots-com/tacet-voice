"""
Audio Device Utilities

Functions for listing, resolving, and managing audio input devices.
"""

import os
import tempfile
from typing import Optional, List, Dict

import numpy as np
import sounddevice as sd
import soundfile as sf


def list_input_devices() -> List[Dict]:
    """
    List all available audio input devices.

    Returns:
        List of dictionaries containing device information:
        - id: Device index
        - name: Device name
        - channels: Max input channels
        - sample_rate: Default sample rate
    """
    devices = sd.query_devices()
    device_list = []
    for i, d in enumerate(devices):
        if d.get("max_input_channels", 0) > 0:
            device_list.append({
                'id': i,
                'name': d.get('name'),
                'channels': d.get('max_input_channels'),
                'sample_rate': d.get('default_samplerate')
            })
    return device_list


def resolve_input_device(audio_cfg: dict) -> Optional[int]:
    """
    Choose audio device by:
      1) audio.sound_device (int) - exact device ID
      2) audio.sound_device (string) - exact-ish name match
      3) audio.sound_device_name - substring match
      4) None - use default input device

    Args:
        audio_cfg: Audio configuration dictionary

    Returns:
        Device ID (int), device name (str), or None for default

    Raises:
        RuntimeError: If sound_device_name specified but not found
    """
    dev = audio_cfg.get("sound_device", None)

    # Exact device ID
    if isinstance(dev, int):
        return dev

    # Device name (exact match)
    if isinstance(dev, str) and dev.strip():
        name = dev.strip().lower()
        devices = sd.query_devices()
        for i, d in enumerate(devices):
            if d.get("max_input_channels", 0) > 0 and name in d.get("name", "").lower():
                return i
        return dev.strip()

    # Device name (substring match)
    name = audio_cfg.get("sound_device_name", None)
    if isinstance(name, str) and name.strip():
        needle = name.strip().lower()
        devices = sd.query_devices()
        for i, d in enumerate(devices):
            if d.get("max_input_channels", 0) > 0 and needle in d.get("name", "").lower():
                return i
        raise RuntimeError(f"No input device matched sound_device_name='{name}'")

    # Use default
    return None


def write_wav(samples: np.ndarray, sr: int) -> str:
    """
    Write audio samples to a temporary WAV file.

    Args:
        samples: Audio samples (numpy array)
        sr: Sample rate (Hz)

    Returns:
        Path to the temporary WAV file
    """
    fd, path = tempfile.mkstemp(suffix=".wav")
    os.close(fd)
    sf.write(path, samples, sr)
    return path
