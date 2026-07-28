"""Diagram renderer — converts PlantUML (.puml) files to SVG for embedding.

PlantUML jar is auto-downloaded on first use if Java is available but no
plantuml installation is found. The jar is cached locally at:
    .cache/plantuml.jar (relative to BookBinder root)
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
import urllib.request
from pathlib import Path

# PlantUML jar download URL (MIT-licensed, stable release)
PLANTUML_JAR_URL = "https://github.com/plantuml/plantuml/releases/download/v1.2024.8/plantuml-1.2024.8.jar"
PLANTUML_JAR_VERSION = "1.2024.8"

# Local cache directory (relative to this file)
_CACHE_DIR = Path(__file__).resolve().parent.parent / ".cache"
_LOCAL_JAR = _CACHE_DIR / "plantuml.jar"

# ANSI color codes for terminal output
_YELLOW = "\033[33m"
_RED = "\033[31m"
_CYAN = "\033[36m"
_DIM = "\033[2m"
_BOLD = "\033[1m"
_RESET = "\033[0m"


def _warn(msg: str) -> None:
    """Print a yellow warning message to stderr."""
    print(f"{_YELLOW}⚠  [BookBinder/PlantUML] {msg}{_RESET}", file=sys.stderr)


def _info(msg: str) -> None:
    """Print an informational message to stderr."""
    print(f"{_CYAN}ℹ  [BookBinder/PlantUML] {msg}{_RESET}", file=sys.stderr)


def _error(msg: str) -> None:
    """Print a red error message to stderr."""
    print(f"{_RED}✗  [BookBinder/PlantUML] {msg}{_RESET}", file=sys.stderr)


def _hint(msg: str) -> None:
    """Print a dim hint/instruction message to stderr."""
    print(f"{_DIM}   {msg}{_RESET}", file=sys.stderr)


def _print_install_instructions() -> None:
    """Print platform-specific installation instructions for Java and PlantUML."""
    print(file=sys.stderr)
    _warn("PlantUML rendering is unavailable. Diagrams will show as placeholders.")
    print(file=sys.stderr)
    _hint("To enable diagram rendering, you need Java (JRE 8+) and PlantUML.")
    _hint("")
    _hint(f"{_BOLD}Option 1: Install Java — PlantUML jar will auto-download{_RESET}")
    _hint("")
    _hint("  Linux (apt):     sudo apt install default-jre")
    _hint("  Linux (yum):     sudo yum install java-17-amazon-corretto-headless")
    _hint("  macOS (brew):    brew install openjdk")
    _hint("  Windows (winget): winget install Microsoft.OpenJDK.17")
    _hint("  Windows (choco):  choco install temurin17jre")
    _hint("")
    _hint(f"{_BOLD}Option 2: Install PlantUML directly{_RESET}")
    _hint("")
    _hint("  Linux (apt):     sudo apt install plantuml")
    _hint("  macOS (brew):    brew install plantuml")
    _hint("  Windows (choco):  choco install plantuml")
    _hint("")
    _hint(f"{_BOLD}Option 3: Set PLANTUML_JAR environment variable{_RESET}")
    _hint("")
    _hint("  Download from: https://plantuml.com/download")
    _hint("  Then: export PLANTUML_JAR=/path/to/plantuml.jar")
    _hint("")
    _hint(f"{_BOLD}Option 4: Pre-render SVGs manually{_RESET}")
    _hint("")
    _hint("  Place .svg files next to .puml files with the same name.")
    _hint("  BookBinder will use pre-rendered SVGs without needing PlantUML.")
    print(file=sys.stderr)


# Track whether we've already printed the install instructions this session
_install_instructions_printed = False


def _ensure_plantuml_jar() -> Path | None:
    """Download the PlantUML jar if not already cached. Returns jar path or None."""
    if _LOCAL_JAR.exists():
        return _LOCAL_JAR

    # Need Java to use the jar
    java = shutil.which("java")
    if not java:
        return None

    # Download
    _CACHE_DIR.mkdir(parents=True, exist_ok=True)
    try:
        _info(f"Downloading PlantUML {PLANTUML_JAR_VERSION} (one-time setup)...")
        _hint(f"  URL: {PLANTUML_JAR_URL}")
        _hint(f"  Cache: {_LOCAL_JAR}")
        urllib.request.urlretrieve(PLANTUML_JAR_URL, str(_LOCAL_JAR))
        _info(f"PlantUML jar cached successfully at: {_LOCAL_JAR}")
        return _LOCAL_JAR
    except (OSError, urllib.error.URLError) as exc:
        _error(f"Failed to download PlantUML jar: {exc}")
        _hint("Check your network connection or download manually from:")
        _hint(f"  {PLANTUML_JAR_URL}")
        _hint(f"Then place it at: {_LOCAL_JAR}")
        # Clean up partial download
        _LOCAL_JAR.unlink(missing_ok=True)
        return None


def find_plantuml() -> list[str] | None:
    """Find a working PlantUML invocation command.

    Checks in order:
    1. PLANTUML_JAR environment variable → java -jar $PLANTUML_JAR
    2. `plantuml` on PATH (e.g. from apt install plantuml)
    3. Common jar locations (system-wide)
    4. Local cached jar (auto-downloaded)

    Returns the command list (e.g. ["java", "-jar", "/path/to/plantuml.jar"])
    or None if not found.
    """
    java = shutil.which("java")

    # 1. Environment variable
    jar_env = os.environ.get("PLANTUML_JAR")
    if jar_env:
        if not Path(jar_env).exists():
            _warn(f"PLANTUML_JAR is set but file not found: {jar_env}")
        elif not java:
            _warn(f"PLANTUML_JAR is set ({jar_env}) but 'java' is not on PATH.")
            _hint("Install a Java Runtime Environment (JRE 8+) to use the jar.")
        else:
            return [java, "-jar", jar_env]

    # 2. plantuml CLI on PATH
    plantuml_cli = shutil.which("plantuml")
    if plantuml_cli:
        return [plantuml_cli]

    # 3. Common jar locations
    if java:
        common_jars = [
            Path.home() / ".local" / "share" / "plantuml" / "plantuml.jar",
            Path.home() / "plantuml.jar",
            Path("/usr/share/plantuml/plantuml.jar"),
            Path("/usr/local/share/plantuml/plantuml.jar"),
            Path("/opt/plantuml/plantuml.jar"),
        ]
        for jar_path in common_jars:
            if jar_path.exists():
                return [java, "-jar", str(jar_path)]

    # 4. Local cached jar (download if needed)
    if java:
        jar = _ensure_plantuml_jar()
        if jar:
            return [java, "-jar", str(jar)]

    return None


def render_puml_to_svg(puml_path: Path, output_dir: Path | None = None) -> Path | None:
    """Render a .puml file to .svg.

    If a .svg with the same stem already exists next to the .puml, returns
    that path without re-rendering (pre-rendered diagrams take priority).

    Args:
        puml_path: Path to the .puml source file.
        output_dir: Directory for the output SVG. Defaults to same dir as puml.

    Returns:
        Path to the rendered .svg file, or None if rendering failed.
    """
    global _install_instructions_printed

    if not puml_path.exists():
        _warn(f"PlantUML source file not found: {puml_path}")
        _hint(f"Expected at: {puml_path.resolve()}")
        return None

    # Check for pre-rendered SVG (same name, .svg extension)
    svg_sibling = puml_path.with_suffix(".svg")
    if svg_sibling.exists():
        return svg_sibling

    # Also check in output_dir if specified
    if output_dir:
        svg_in_output = output_dir / (puml_path.stem + ".svg")
        if svg_in_output.exists():
            return svg_in_output

    # Try to render
    cmd = find_plantuml()
    if cmd is None:
        _warn(f"Cannot render diagram: {puml_path.name}")

        # Diagnose the specific problem
        java = shutil.which("java")
        if not java:
            _warn("Root cause: Java Runtime Environment (JRE) not found on PATH.")
            _hint("PlantUML requires Java 8 or later to run.")
        else:
            _warn("Root cause: PlantUML jar not found and auto-download failed.")
            _hint(f"Java found at: {java}")
            _hint("But no PlantUML installation could be located or downloaded.")

        # Print full install instructions (only once per session)
        if not _install_instructions_printed:
            _print_install_instructions()
            _install_instructions_printed = True
        else:
            _hint("(Install instructions printed above — scroll up)")

        return None

    target_dir = output_dir or puml_path.parent
    target_dir.mkdir(parents=True, exist_ok=True)

    try:
        render_cmd = cmd + [
            "-tsvg",
            "-o", str(target_dir),
            str(puml_path),
        ]
        result = subprocess.run(
            render_cmd,
            capture_output=True,
            text=True,
            timeout=120,  # Large diagrams can take a while
        )
        if result.returncode == 0:
            expected_svg = target_dir / (puml_path.stem + ".svg")
            if expected_svg.exists():
                # Check for warnings in output even on success
                if result.stderr and "error" in result.stderr.lower():
                    _warn(f"PlantUML produced output but reported issues for: {puml_path.name}")
                    for line in result.stderr.strip().split("\n")[:3]:
                        _hint(f"  {line}")
                return expected_svg

            # PlantUML may have used the @startuml name instead of the filename.
            # Scan for any new .svg file in the target directory that wasn't there before,
            # or look for the diagram name in the .puml file.
            import re
            puml_text = puml_path.read_text(encoding="utf-8", errors="replace")
            m = re.search(r"@startuml\s+(\S+)", puml_text)
            if m:
                diagram_name = m.group(1)
                alt_svg = target_dir / (diagram_name + ".svg")
                if alt_svg.exists():
                    # Rename to match the source filename for consistency
                    _warn(f"PlantUML used diagram name '{diagram_name}' instead of filename '{puml_path.stem}'.")
                    _hint(f"  Renaming: {alt_svg.name} → {expected_svg.name}")
                    _hint(f"  Tip: Remove the name from @startuml to avoid this.")
                    _hint(f"       Change '@startuml {diagram_name}' to just '@startuml'")
                    alt_svg.rename(expected_svg)
                    return expected_svg

            # Last resort: find any SVG that appeared in target_dir
            all_svgs = list(target_dir.glob("*.svg"))
            if all_svgs:
                # If there's exactly one SVG and it's new, use it
                _warn(f"PlantUML ran successfully but SVG not at expected path:")
                _hint(f"  Expected: {expected_svg.name}")
                _hint(f"  Found:    {', '.join(s.name for s in all_svgs)}")
                _hint(f"  Tip: Remove the diagram name from @startuml in {puml_path.name}")
                # Rename the most likely candidate
                for svg in all_svgs:
                    if puml_path.stem.replace("_", "").lower() in svg.stem.replace("_", "").lower():
                        svg.rename(expected_svg)
                        return expected_svg
                return None
            else:
                _warn(f"PlantUML ran successfully but no SVG output found.")
                _hint(f"  Expected: {expected_svg}")
                _hint(f"  Target dir: {target_dir}")
                return None
        else:
            _warn(f"PlantUML rendering failed for: {puml_path.name}")
            _hint(f"  Exit code: {result.returncode}")
            if result.stderr:
                # Show first few lines of stderr
                stderr_lines = result.stderr.strip().split("\n")
                for line in stderr_lines[:8]:
                    _hint(f"  stderr: {line}")
                if len(stderr_lines) > 8:
                    _hint(f"  ... ({len(stderr_lines) - 8} more lines)")
            if result.stdout:
                stdout_lines = result.stdout.strip().split("\n")
                for line in stdout_lines[:4]:
                    _hint(f"  stdout: {line}")
            _hint("")
            _hint("Common causes:")
            _hint("  • Syntax error in the .puml file")
            _hint("  • Diagram too large (increase timeout or simplify)")
            _hint("  • Missing fonts (install fonts or use default)")
            _hint(f"  • Try manually: {' '.join(render_cmd)}")
            return None

    except subprocess.TimeoutExpired:
        _warn(f"PlantUML rendering timed out (>120s) for: {puml_path.name}")
        _hint("The diagram may be too complex for the default timeout.")
        _hint("Try rendering manually to check:")
        _hint(f"  {' '.join(cmd)} -tsvg -o {target_dir} {puml_path}")
        return None
    except OSError as exc:
        _error(f"Failed to execute PlantUML command: {exc}")
        _hint(f"  Command: {' '.join(cmd)}")
        _hint("  Check that Java is properly installed and accessible.")
        return None


def can_render_diagrams() -> bool:
    """Check if PlantUML rendering is available."""
    return find_plantuml() is not None


def diagnose() -> str:
    """Return a diagnostic string describing the PlantUML setup status.

    Useful for debugging or displaying in a --verbose mode.
    """
    lines: list[str] = []
    lines.append("PlantUML Diagnostic Report")
    lines.append("=" * 40)

    # Java check
    java = shutil.which("java")
    if java:
        lines.append(f"✓ Java found: {java}")
        try:
            ver = subprocess.run(
                [java, "-version"], capture_output=True, text=True, timeout=5
            )
            version_line = (ver.stderr or ver.stdout).strip().split("\n")[0]
            lines.append(f"  Version: {version_line}")
        except (subprocess.TimeoutExpired, OSError):
            lines.append("  Version: (could not determine)")
    else:
        lines.append("✗ Java NOT found on PATH")
        lines.append("  PlantUML requires Java 8+ (JRE or JDK)")

    # PLANTUML_JAR env
    jar_env = os.environ.get("PLANTUML_JAR")
    if jar_env:
        exists = Path(jar_env).exists()
        status = "✓ exists" if exists else "✗ NOT FOUND"
        lines.append(f"  PLANTUML_JAR={jar_env} ({status})")
    else:
        lines.append("  PLANTUML_JAR not set")

    # plantuml CLI
    plantuml_cli = shutil.which("plantuml")
    if plantuml_cli:
        lines.append(f"✓ plantuml CLI found: {plantuml_cli}")
    else:
        lines.append("  plantuml CLI not on PATH")

    # Cached jar
    if _LOCAL_JAR.exists():
        size_mb = _LOCAL_JAR.stat().st_size / (1024 * 1024)
        lines.append(f"✓ Cached jar: {_LOCAL_JAR} ({size_mb:.1f} MB)")
    else:
        lines.append(f"  Cached jar not present: {_LOCAL_JAR}")

    # Overall status
    cmd = find_plantuml()
    lines.append("")
    if cmd:
        lines.append(f"✓ PlantUML rendering AVAILABLE")
        lines.append(f"  Command: {' '.join(cmd)}")
    else:
        lines.append("✗ PlantUML rendering UNAVAILABLE")
        lines.append("  Diagrams will appear as placeholders in the PDF.")

    return "\n".join(lines)