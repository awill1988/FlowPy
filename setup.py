"""
A basic top-level setup.py script that delegates to the real one in
src/setup.py

This is used to generate the source package for distribution on PyPI.
"""

from pathlib import Path
import sys

sys.path.insert(0, str((Path(__file__).parent / "src").resolve()))
from src.setup import *
