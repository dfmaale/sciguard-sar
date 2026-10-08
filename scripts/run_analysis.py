#!/usr/bin/env python3
"""Run available experiments without a Jupyter dependency."""
import argparse,sys,os
from pathlib import Path
os.environ.setdefault("OMP_NUM_THREADS","1")
os.environ.setdefault("OPENBLAS_NUM_THREADS","1")
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
from threadpoolctl import threadpool_limits
from sciguard.experiments import AnalysisRun,RunConfig,SECTIONS

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--profile",choices=["smoke","full"],default="smoke")
    parser.add_argument("--sections",nargs="+",choices=list(SECTIONS),default=list(SECTIONS))
    args=parser.parse_args()
    config=RunConfig.smoke() if args.profile=="smoke" else RunConfig()
    with threadpool_limits(limits=1):
        run=AnalysisRun(ROOT,config)
        for name in args.sections: run.section(name,SECTIONS[name])
        if args.sections==list(SECTIONS): run.finish()
        print(run.out)

if __name__=="__main__": main()
