#!/usr/bin/env python3
"""Render an existing full run without rerunning experiments or changing its manifest."""
from pathlib import Path
from types import SimpleNamespace
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
from sciguard.plotting import generate_all
run=SimpleNamespace(out=ROOT/"results/full",fig=ROOT/"figures/full")
print(generate_all(run))
