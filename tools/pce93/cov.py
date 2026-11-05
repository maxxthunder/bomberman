"""Coverage runs for the dead-code sweep: python tools/pce93/cov.py <us|jp|sp> <name> <outroot> "<lua segment calls>"
Runs tools/pce93/cov.lua plus the given segments in Mesen (MESEN = a portable copy; its Debugger folder is removed
first so the log holds this run only) and leaves <outroot>/<ver>_<name>/cov.cdl. Password helpers: pw(ver, **state)
gives the grid indices for play()/gameover()/ending()."""
import os, sys, shutil, subprocess
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from password import encode, LETTERS
def pw(ver, **st):
    v = "jp" if ver == "sp" else ver
    return "{" + ",".join(str(LETTERS[v].index(c)) for c in encode(v, **st)) + "}"
if __name__ == "__main__":
    ver, name, root, segs = sys.argv[1:5]
    d = os.path.join(root, f"{ver}_{name}"); os.makedirs(d, exist_ok=True)
    shutil.rmtree(os.path.join(os.path.dirname(os.environ["MESEN"]), "Debugger"), ignore_errors=True)
    off = -9 if ver == "sp" else 0
    open(os.path.join(d, "x.lua"), "w").write(f"VER='{ver}' OFF={off}\n" + open(os.path.join(HERE, "cov.lua")).read() + "\n" + segs + "\ncdl_dump('cov') wn_dump()\n")
    out = subprocess.run(["sh", os.path.join(HERE, "run.sh"), os.path.join(d, "x.lua"), ver], capture_output=True, text=True).stdout
    open(os.path.join(d, "log.txt"), "w").write(out); print(ver, name, out[-300:])
