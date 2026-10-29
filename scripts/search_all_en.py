#!/usr/bin/env python3
import subprocess, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
cats = sys.argv[1:] or [f"{i:02d}" for i in range(1,13)]
for c in cats:
    print(f"\n===== SEARCH {c} =====", flush=True)
    r = subprocess.run([sys.executable, "-I", str(ROOT/"scripts/papers_en.py"), "search", c, "--per-query", "40"], cwd=str(ROOT))
    if r.returncode:
        sys.exit(r.returncode)
print("ALL SEARCH DONE")
