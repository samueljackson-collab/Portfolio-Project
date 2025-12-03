#!/usr/bin/env python3
import json, subprocess, pathlib, re, time
out = subprocess.check_output(["bash","scripts/portfolio-status.sh"], text=True, stderr=subprocess.STDOUT)
lines = [l for l in out.splitlines() if re.search(r"^P[0-9]{2}-", l)]
rows = []
for l in lines:
    parts = l.split()
    rows.append({"project": parts[0], "code": parts[1], "doc": parts[2], "diag": parts[3], "test": parts[4], "obs": parts[5]})
md = ["# Portfolio Status (auto)", "", f"_generated: {time.strftime('%Y-%m-%d %H:%M:%S')}_", "", "| Project | Code | Doc | Diagram | Test | Obs |", "|---|:---:|:---:|:---:|:---:|:---:|"]
for r in rows:
    md.append(f"| {r['project']} | {r['code']} | {r['doc']} | {r['diag']} | {r['test']} | {r['obs']} |")
path = pathlib.Path("docs/status.md"); path.parent.mkdir(exist_ok=True)
path.write_text("\n".join(md))
print("wrote", path)
