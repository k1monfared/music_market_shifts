"""Regenerate the report figures (PNGs in docs/images/) from committed data."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src import figures


def main() -> None:
    paths = figures.generate_all()
    print("Generated figures:")
    for key, path in paths.items():
        print(f"  {key:14s} -> {path}")


if __name__ == "__main__":
    main()
