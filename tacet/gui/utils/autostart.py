"""
Auto-Start Functionality

Cross-platform auto-start on system boot.
"""

import os
import sys
import platform
import subprocess
from pathlib import Path

from tacet.gui.utils.platform_utils import get_app_name, get_app_path


def enable_auto_start():
    """Enable auto-start on system boot (cross-platform)"""
    system = platform.system()

    if system == "Windows":
        _enable_auto_start_windows()
    elif system == "Darwin":  # macOS
        _enable_auto_start_macos()
    elif system == "Linux":
        _enable_auto_start_linux()
    else:
        raise Exception(f"Unsupported platform: {system}")


def disable_auto_start():
    """Disable auto-start on system boot (cross-platform)"""
    system = platform.system()

    if system == "Windows":
        _disable_auto_start_windows()
    elif system == "Darwin":  # macOS
        _disable_auto_start_macos()
    elif system == "Linux":
        _disable_auto_start_linux()
    else:
        raise Exception(f"Unsupported platform: {system}")


def _enable_auto_start_windows():
    """Enable auto-start on Windows via Startup folder"""
    import winshell
    from win32com.client import Dispatch

    app_name = get_app_name()
    app_path = get_app_path()

    # Get startup folder
    startup_folder = winshell.startup()
    shortcut_path = os.path.join(startup_folder, f"{app_name}.lnk")

    # Create shortcut
    shell = Dispatch('WScript.Shell')
    shortcut = shell.CreateShortCut(shortcut_path)
    shortcut.Targetpath = sys.executable  # Python executable
    shortcut.Arguments = f'"{app_path}"'
    shortcut.WorkingDirectory = os.path.dirname(app_path)
    shortcut.IconLocation = sys.executable
    shortcut.save()


def _disable_auto_start_windows():
    """Disable auto-start on Windows"""
    import winshell

    app_name = get_app_name()
    startup_folder = winshell.startup()
    shortcut_path = os.path.join(startup_folder, f"{app_name}.lnk")

    if os.path.exists(shortcut_path):
        os.remove(shortcut_path)


def _enable_auto_start_macos():
    """Enable auto-start on macOS via LaunchAgent"""
    app_name = get_app_name()
    app_path = get_app_path()

    # LaunchAgents directory
    launch_agents_dir = Path.home() / "Library" / "LaunchAgents"
    launch_agents_dir.mkdir(parents=True, exist_ok=True)

    plist_path = launch_agents_dir / f"com.{app_name}.plist"

    # Create plist content
    plist_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.{app_name}</string>
    <key>ProgramArguments</key>
    <array>
        <string>{sys.executable}</string>
        <string>{app_path}</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <false/>
    <key>StandardOutPath</key>
    <string>/tmp/{app_name}.log</string>
    <key>StandardErrorPath</key>
    <string>/tmp/{app_name}.err</string>
</dict>
</plist>
"""

    # Write plist file
    with open(plist_path, "w") as f:
        f.write(plist_content)

    # Load the launch agent
    subprocess.run(["launchctl", "load", str(plist_path)], check=False)


def _disable_auto_start_macos():
    """Disable auto-start on macOS"""
    app_name = get_app_name()
    launch_agents_dir = Path.home() / "Library" / "LaunchAgents"
    plist_path = launch_agents_dir / f"com.{app_name}.plist"

    if plist_path.exists():
        # Unload the launch agent
        subprocess.run(["launchctl", "unload", str(plist_path)], check=False)
        # Remove the plist file
        plist_path.unlink()


def _enable_auto_start_linux():
    """Enable auto-start on Linux via .desktop file"""
    app_name = get_app_name()
    app_path = get_app_path()

    # Autostart directory
    autostart_dir = Path.home() / ".config" / "autostart"
    autostart_dir.mkdir(parents=True, exist_ok=True)

    desktop_path = autostart_dir / f"{app_name}.desktop"

    # Create .desktop file content
    desktop_content = f"""[Desktop Entry]
Type=Application
Name={app_name}
Exec={sys.executable} "{app_path}"
Hidden=false
NoDisplay=false
X-GNOME-Autostart-enabled=true
Comment=Tacet
"""

    # Write .desktop file
    with open(desktop_path, "w") as f:
        f.write(desktop_content)

    # Make it executable
    desktop_path.chmod(0o755)


def _disable_auto_start_linux():
    """Disable auto-start on Linux"""
    app_name = get_app_name()
    autostart_dir = Path.home() / ".config" / "autostart"
    desktop_path = autostart_dir / f"{app_name}.desktop"

    if desktop_path.exists():
        desktop_path.unlink()
