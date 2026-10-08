#!/usr/bin/env python3
"""Execute only the credentialed-data protocol, using explicit local arguments."""
from pathlib import Path
import sys,argparse,json
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
from threadpoolctl import threadpool_limits
from sciguard.mimic import run_mimic
from sciguard.plotting import mimic_decision_map
import matplotlib.pyplot as plt
parser=argparse.ArgumentParser()
parser.add_argument("--data",required=True)
parser.add_argument("--config",default=str(ROOT/"config/mimic_protocol.json"))
args=parser.parse_args()
with threadpool_limits(limits=1):
    tables,manifest=run_mimic(args.data,json.loads(Path(args.config).read_text()),ROOT/"results/mimic_local")
    fig=mimic_decision_map(tables["mimic_results"],ROOT/"figures/mimic_local")
    plt.close(fig)
print(manifest["status"])
