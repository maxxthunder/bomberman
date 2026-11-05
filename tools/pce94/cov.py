"""Coverage runs for the dead-code sweep: python tools/pce94/cov.py <card|demo> <name> "<lua segment calls>" [VAR=v ...]
Needs SCRATCH (as run.sh) and MESEN = a portable Mesen copy; its Debugger folder is removed first so the code/data
log holds this run only. Leaves $SCRATCH/cov_<name>_<game>/cov.bin."""
import os, sys, shutil, subprocess
HERE = os.path.dirname(os.path.abspath(__file__))
g, name, segs = sys.argv[1:4]
shutil.rmtree(os.path.join(os.path.dirname(os.environ["MESEN"]), "Debugger"), ignore_errors=True)
d = os.path.join(os.environ["SCRATCH"], "covsrc"); os.makedirs(d, exist_ok=True)
f = os.path.join(d, f"cov_{name}.lua")
open(f, "w").write(open(os.path.join(HERE, "cov.lua")).read() + "\n" + segs + "\ncdl_dump('cov') wn_dump()\n")
p = subprocess.run(["sh", os.path.join(HERE, "run.sh"), f, g] + sys.argv[4:], capture_output=True, text=True)
print(name, p.stdout[-400:], p.stderr[-400:])
