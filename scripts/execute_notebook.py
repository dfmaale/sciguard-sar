#!/usr/bin/env python3
"""Execute notebook cells in a fresh process, without requiring kernel sockets.

The default uses an in-process IPython shell, preserving cell order and capturing
real rich outputs. --backend jupyter uses nbclient where kernel sockets are allowed.
Execution metadata identifies the backend; failures stop execution and are saved.
"""
import os,sys,argparse,io,base64,traceback,time
os.environ.setdefault("OMP_NUM_THREADS","1")
os.environ.setdefault("OPENBLAS_NUM_THREADS","1")
os.environ.setdefault("MPLBACKEND","Agg")
from pathlib import Path
import nbformat
ROOT=Path(__file__).resolve().parents[1]
path=ROOT/"SciGuard_JMLR_Reproducible_Analysis_MIMIC_IV.ipynb"


def main():
    parser=argparse.ArgumentParser(); parser.add_argument("--backend",choices=["inprocess","jupyter"],default="inprocess")
    args=parser.parse_args(); nb=nbformat.read(path,as_version=4)
    os.chdir(ROOT)
    for cell in nb.cells:
        if cell.cell_type=="code": cell.outputs=[]; cell.execution_count=None
    nb.metadata["sciguard"]["execution_backend"]=args.backend
    nb.metadata["sciguard"]["execution_status"]="running"
    start=time.perf_counter()
    try:
        if args.backend=="jupyter":
            from nbclient import NotebookClient
            NotebookClient(nb,timeout=1800,kernel_name="python3",resources={"metadata":{"path":str(ROOT)}},allow_errors=False).execute()
        else:
            from IPython.core.interactiveshell import InteractiveShell
            from IPython.utils.capture import capture_output
            from matplotlib.figure import Figure
            shell=InteractiveShell.instance()
            def figure_png(figure):
                buf=io.BytesIO(); figure.savefig(buf,format="png",dpi=120,bbox_inches="tight")
                return buf.getvalue()
            shell.display_formatter.formatters["image/png"].for_type(Figure,figure_png)
            count=0
            for index,cell in enumerate(nb.cells):
                if cell.cell_type!="code": continue
                count+=1; print(f"Executing cell {index} (code {count})",flush=True)
                with capture_output(stdout=True,stderr=True,display=True) as captured:
                    result=shell.run_cell(cell.source,store_history=True)
                cell.execution_count=count
                if captured.stdout: cell.outputs.append(nbformat.v4.new_output("stream",name="stdout",text=captured.stdout))
                if captured.stderr: cell.outputs.append(nbformat.v4.new_output("stream",name="stderr",text=captured.stderr))
                for rich in captured.outputs:
                    data={k:base64.b64encode(v).decode("ascii") if isinstance(v,bytes) else v for k,v in rich.data.items()}
                    cell.outputs.append(nbformat.v4.new_output("display_data",data=data,metadata=rich.metadata))
                error=result.error_before_exec or result.error_in_exec
                if error:
                    cell.outputs.append(nbformat.v4.new_output("error",ename=type(error).__name__,evalue=str(error),traceback=traceback.format_exception(error)))
                    raise error
                nbformat.write(nb,path)
        nb.metadata["sciguard"]["execution_status"]="completed"
        nb.metadata["sciguard"]["execution_seconds"]=time.perf_counter()-start
    except Exception:
        nb.metadata["sciguard"]["execution_status"]="failed"
        raise
    finally:
        nbformat.write(nb,path)
    nbformat.validate(nb)
    print("Executed",sum(c.cell_type=="code" for c in nb.cells),"code cells successfully.")

if __name__=="__main__": main()
