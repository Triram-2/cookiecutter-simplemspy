"""Hook executed before project generation."""

from __future__ import annotations

from pathlib import Path


PROJECT_DIRECTORY = Path.cwd()


def main() -> None:
    """Placeholder pre-generation logic."""
    pass

if __name__ == "__main__":
    main()
