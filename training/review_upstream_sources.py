#!/usr/bin/env python3
"""Parallel upstream source snapshots for license review; never import/execute code."""
import concurrent.futures
import json
import os
import pathlib
import subprocess
import sys
import tempfile
from datetime import datetime, timezone

UPSTREAMS = [
    "vespCV/hornet3000", "vespCV/vespcv", "andrw3000/vespai",
    "jeroen-kanters/Hornet_Trap", "PauMonterosa/vespa-velutina-tracker",
    "philippkueng/auditive_detection_of_asian_hornets", "mbron64/buzzhive-open",
    "MacNite/HiveHub", "jodivaso/varrodetector",
    "WataNekko/aiot-beehive", "gitDew/waspinator",
    "divednakumari-lab/beehive-monitor",
]

def inspect(name, root):
    owner, project = name.split("/")
    target = root / owner / project
    target.parent.mkdir(parents=True, exist_ok=True)
    result = {"repository": name, "url": f"https://github.com/{name}",
              "cloned": False, "source_integrated": False,
              "license_approved": False, "models_approved": False,
              "datasets_approved": False}
    try:
        command = ["git", "-c", "protocol.file.allow=never", "clone", "--depth", "1",
                   "--filter=blob:none", "--no-checkout",
                   f"https://github.com/{name}.git", str(target)]
        subprocess.run(command, check=True, capture_output=True, text=True, timeout=120,
                       env={**os.environ, "GIT_TERMINAL_PROMPT": "0"})
        sha = subprocess.run(["git", "-C", str(target), "rev-parse", "HEAD"],
                             check=True, capture_output=True, text=True, timeout=15).stdout.strip()
        result.update(cloned=True, commit=sha, review_status="awaiting_per-file_license_review")
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired, OSError) as exc:
        result.update(error=str(exc)[:500], review_status="clone_failed")
    return result

def main():
    output = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "training/upstream-source-review.json")
    with tempfile.TemporaryDirectory(prefix="vespaguard-upstream-") as temp:
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
            records = list(pool.map(lambda name: inspect(name, pathlib.Path(temp)), UPSTREAMS))
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps({"generated_at": datetime.now(timezone.utc).isoformat(),
        "purpose": "isolated source review only", "upstreams": records}, indent=2) + "\n")
    print(f"Source snapshots: {sum(x['cloned'] for x in records)}/{len(records)}; no source merged")
    for item in records:
        print(f"{item['repository']}: {item['review_status']}")
    # Fail if every source fails, without bypassing license gates.
    if not any(x["cloned"] for x in records):
        sys.exit(1)

if __name__ == "__main__":
    main()
