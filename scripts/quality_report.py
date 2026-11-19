#!/usr/bin/env python3
"""Generate an evidence-based project quality snapshot; never mark untested AI as ready."""
from pathlib import Path
import json
import os
from datetime import datetime, timezone

ROOT=Path(__file__).resolve().parents[1]
sources=json.loads((ROOT/"sources/catalog.json").read_text(encoding="utf-8"))["sources"]
modules=["hornet","varroa","brood","pollen","swarm","queen"]
counts={name:sum(name in source["modules"] for source in sources) for name in modules}
ready={name:False for name in modules}
lines=[
"# Beekeeper Monitor – automated quality snapshot",
"",
f"Generated: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}",
"",
"## Verified from repository contents (not device tests)",
"",
f"- Research candidates documented: **{len(sources)}** (none approved solely by catalog inclusion)",
f"- Static PWA entrypoint present: **{(ROOT/'index.html').is_file()}**",
f"- Offline service worker present: **{(ROOT/'sw.js').is_file()}**",
f"- Browser integration test file present: **{(ROOT/'tests/browser.spec.cjs').is_file()}**",
"",
"## AI readiness (requires actual weights and independent evaluation)",
"",
"| Module | Candidate sources | Approved for production |",
"|---|---:|---|",
]
for name in modules:
    lines.append(f"| {name} | {counts[name]} | NO – unvalidated |")
lines += [
"",
"## External verification not established by this script",
"",
"- GitHub Pages deployment success",
"- Real iPhone/Android install, camera and offline behavior",
"- Precision, recall and field reliability of six AI tasks",
"- SMS/push alerts, audio inference and multi-device triangulation",
"",
"**A passing CI job validates code checks, not field-ready AI or 99% accuracy.**",
]
report="\n".join(lines)+"\n"
out=ROOT/"quality-report.md"
out.write_text(report,encoding="utf-8")
print(report)
if os.environ.get("GITHUB_STEP_SUMMARY"):
    with open(os.environ["GITHUB_STEP_SUMMARY"],"a",encoding="utf-8") as f:f.write(report)
