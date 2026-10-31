"""Regenerates the synthetic demo data. Same as: python -m benchmark demo-data"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from benchmark.cli import main  # noqa: E402

sys.exit(main(["demo-data"]))
