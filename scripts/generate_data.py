"""Generate the synthetic listening dataset (CSVs in data/)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src import data_gen


def main() -> None:
    written = data_gen.save_dataset()
    print("Generated synthetic data (synthetic, for demonstration only):")
    for key, path in written.items():
        print(f"  {key:8s} -> {path}")


if __name__ == "__main__":
    main()
