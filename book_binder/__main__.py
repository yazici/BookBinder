"""Allow running as: python -m book_binder BOOK.md"""

import sys
from pathlib import Path

# Ensure the parent directory is on the path
sys.path.insert(0, str(Path(__file__).parent.parent))

from book_binder.maker import BookMaker
from book_binder.templates import available_templates, available_themes

# Reuse the CLI from make_a_book.py
if __name__ == "__main__":
    # Import and run the main CLI
    sys.path.insert(0, str(Path(__file__).parent.parent))
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "make_a_book",
        Path(__file__).parent.parent / "make_a_book.py"
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
