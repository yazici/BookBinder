"""Dependency bootstrap — ensures Python packages and Playwright Chromium are installed."""

from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path


def _run(args: list[str], *, check: bool = True, capture: bool = False) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(args, text=True, capture_output=capture)
    if check and result.returncode != 0:
        detail = result.stderr.strip() if capture and result.stderr else ""
        raise RuntimeError(
            f"Command failed ({result.returncode}): {subprocess.list2cmdline(args)}"
            + (f"\n{detail}" if detail else "")
        )
    return result


def ensure_packages(force: bool = False) -> None:
    """Install missing Python packages (or upgrade all if force=True)."""
    required = {
        "markdown": "markdown",
        "jinja2": "jinja2",
        "playwright": "playwright",
        "yaml": "pyyaml",
        "pygments": "pygments",
    }
    missing = [pkg for mod, pkg in required.items() if importlib.util.find_spec(mod) is None]
    if not force and not missing:
        return

    # Ensure pip is available
    probe = _run([sys.executable, "-m", "pip", "--version"], check=False, capture=True)
    if probe.returncode != 0:
        _run([sys.executable, "-m", "ensurepip", "--upgrade"])

    packages = sorted(set(required.values())) if force else missing
    print(f"[BookBinder] Installing: {', '.join(packages)}")
    cmd = [sys.executable, "-m", "pip", "install"]
    if force:
        cmd.append("--upgrade")
    _run(cmd + packages)
    importlib.invalidate_caches()


def chromium_path() -> Path | None:
    """Check if Playwright Chromium is installed and return its path."""
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as pw:
            candidate = Path(pw.chromium.executable_path)
            return candidate if candidate.is_file() else None
    except Exception:
        return None


def ensure_chromium(force: bool = False) -> None:
    """Install Playwright Chromium if not present (or reinstall if force=True)."""
    current = chromium_path()
    if current and not force:
        return
    print("[BookBinder] Installing Playwright Chromium...")
    _run([sys.executable, "-m", "playwright", "install", "chromium"])


def bootstrap(force: bool = False) -> None:
    """Full bootstrap: packages + Chromium."""
    ensure_packages(force)
    ensure_chromium(force)