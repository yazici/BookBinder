<!-- @chapter: Installation -->

<!-- @index-term: installation -->
<!-- @index-term: bootstrap -->

# Installation

BookBinder converts Markdown files into professionally formatted PDFs. This chapter covers every way to get it running on your system.

## Prerequisites

BookBinder requires:

| Component | Minimum Version | Purpose |
|-----------|----------------|---------|
| Python | 3.10+ | Core runtime |
| pip | Latest | Package management |
| Chromium | (via Playwright) | PDF rendering engine |
| Java | 11+ *(optional)* | PlantUML diagram rendering |

<!-- @note: BookBinder uses Playwright's bundled Chromium for PDF generation — you do not need Chrome or Chromium installed system-wide. -->

## Quick Start (Self-Bootstrap)

The fastest way to get running is BookBinder's built-in bootstrap command:

```bash
python make_a_book.py --self-bootstrap
```

This single command will:

1. Check for missing Python packages
2. Install `markdown`, `jinja2`, `playwright`, `pyyaml`, and `pygments`
3. Download and install Playwright's Chromium browser

After bootstrap completes, you can immediately build books.

<!-- @tip: If you already have the dependencies but want to upgrade them all, use `--force-dependencies` instead. -->

## Full Bootstrap Script

For a fresh system where Python itself may not be installed, use the standalone bootstrap script:

```bash
git clone https://github.com/yazici/BookBinder.git
cd BookBinder
chmod +x bootstrap.sh
./bootstrap.sh
```

### Bootstrap Options

| Flag | Effect |
|------|--------|
| `--minimal` | Skip optional tools (Java/PlantUML) |
| `--upgrade` | Force-upgrade all Python dependencies |
| `--help` | Show usage information |

### What the Script Does

The bootstrap script performs these steps in order:

1. **Detects your OS and package manager** — supports apt, dnf, yum, pacman, zypper (Linux) and Homebrew (macOS)
2. **Installs Python 3.10+** — if not already present
3. **Ensures pip is available** — uses `ensurepip` or downloads `get-pip.py`
4. **Installs Python packages** — `markdown`, `jinja2`, `playwright`, `pyyaml`, `pygments`
5. **Installs Playwright Chromium** — including system dependencies on Linux
6. **Installs Java** *(unless `--minimal`)* — for PlantUML diagram rendering
7. **Verifies everything** — runs checks and reports status

<!-- @important: On Linux, Playwright's system dependency installation (`playwright install-deps`) requires sudo. The script will prompt for your password. -->

## Manual Installation

If you prefer to install components yourself:

```bash
# 1. Install Python packages
pip install markdown jinja2 playwright pyyaml pygments

# 2. Install Playwright Chromium
python -m playwright install chromium

# 3. (Optional) Install Java for PlantUML
# Debian/Ubuntu:
sudo apt install default-jre-headless
# macOS:
brew install openjdk
```

## Installation from Git

```bash
git clone https://github.com/yazici/BookBinder.git
cd BookBinder
python make_a_book.py --self-bootstrap
```

BookBinder is a standalone tool — no `setup.py` or `pip install -e .` required. Just clone and run `make_a_book.py` from the repository root.

## Verifying Your Installation

Run the following to confirm everything is working:

```bash
# Check Python version
python3 --version

# Check that all imports work
python3 -c "import markdown, jinja2, playwright, yaml, pygments; print('All OK')"

# Check Playwright Chromium
python3 -c "
from playwright.sync_api import sync_playwright
from pathlib import Path
with sync_playwright() as pw:
    p = Path(pw.chromium.executable_path)
    print(f'Chromium: {p}')
    assert p.is_file(), 'Chromium not found!'
print('Playwright OK')
"

# List available templates and themes
python3 make_a_book.py --list-templates
python3 make_a_book.py --list-themes
```

## Platform Notes

### Linux

On Debian/Ubuntu, Playwright requires several system libraries for Chromium. The bootstrap script handles this automatically via `playwright install-deps`. If you install manually, run:

```bash
sudo python3 -m playwright install-deps chromium
```

### macOS

Homebrew is required for the bootstrap script. Install it from [brew.sh](https://brew.sh) if not present. Python 3.12 is recommended:

```bash
brew install python@3.12
```

### Windows (WSL)

BookBinder runs under Windows Subsystem for Linux. Use the same Linux instructions inside your WSL distribution. Native Windows is not currently supported.

<!-- @warning: Running BookBinder directly on Windows (outside WSL) is not supported due to Playwright Chromium path differences. Use WSL2 with Ubuntu for the best experience. -->

## Updating BookBinder

To update to the latest version:

```bash
cd BookBinder
git pull
python make_a_book.py --force-dependencies
```

This pulls the latest code and upgrades all Python dependencies.