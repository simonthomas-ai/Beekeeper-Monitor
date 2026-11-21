#!/usr/bin/env python3
"""Report observed GitHub Actions job time, never estimated AI-agent work."""
import datetime as dt
import json
import os
import urllib.request

REPO = os.environ.get("GITHUB_REPOSITORY", "")
TOKEN = os.environ.get("GITHUB_TOKEN", "")
if not REPO or not TOKEN:
    raise SystemExit("GITHUB_REPOSITORY and GITHUB_TOKEN required")
now = dt.datetime.now(dt.timezone.utc)
since = now - dt.timedelta(days=7)

def request(path):
    req = urllib.request.Request(
        "https://api.github.com" + path,
        headers={"Authorization": "Bearer " + TOKEN,
                 "Accept": "application/vnd.github+json",
                 "X-GitHub-Api-Version": "2022-11-28",
                 "User-Agent": "VespaGuard-activity-report"})
    with urllib.request.urlopen(req, timeout=30) as response:
        return json.load(response)

def stamp(value):
    return dt.datetime.fromisoformat(value.replace("Z", "+00:00"))

runs = []
for page in range(1, 6):
    data = request(f"/repos/{REPO}/actions/runs?per_page=100&page={page}&created=>={since.date().isoformat()}")
    batch = data.get("workflow_runs", [])
    runs.extend(x for x in batch if stamp(x["created_at"]) >= since)
    if len(batch) < 100:
        break
runs = sorted(runs, key=lambda x: x["created_at"], reverse=True)
completed = [r for r in runs if r["status"] == "completed"]
jobs_seconds = 0
jobs_count = 0
# Cap detailed job queries and explicitly disclose partial coverage.
sample = completed[:40]
for run in sample:
    for page in range(1, 6):
        data = request(f"/repos/{REPO}/actions/runs/{run['id']}/jobs?per_page=100&page={page}")
        batch = data.get("jobs", [])
        for job in batch:
            if job.get("started_at") and job.get("completed_at"):
                jobs_seconds += max(0, (stamp(job["completed_at"]) - stamp(job["started_at"])).total_seconds())
                jobs_count += 1
        if len(batch) < 100:
            break
report = [
    "# VespaGuard: automatische Aktivitäts- und Zeitmessung",
    "",
    f"Erstellt: {now.isoformat(timespec='seconds')}",
    f"Zeitraum: letzte 7 Tage ab {since.isoformat(timespec='seconds')}",
    "",
    f"- Erfasste Workflow-Läufe: **{len(runs)}**",
    f"- Abgeschlossene Workflow-Läufe: **{len(completed)}**",
    f"- Davon erfolgreiche Läufe: **{sum(r.get('conclusion') == 'success' for r in completed)}**",
    f"- Davon fehlgeschlagene Läufe: **{sum(r.get('conclusion') == 'failure' for r in completed)}**",
    f"- Erfasste Jobs mit Zeitstempeln: **{jobs_count}** aus **{len(sample)}** abgeschlossenen Läufen",
    f"- Summe der Job-Laufzeiten: **{jobs_seconds / 3600:.2f} Job-Stunden**",
    "",
    "**Wichtig:** Job-Stunden sind addierte GitHub-Actions-Jobzeiten, keine Arbeitsstunden von KI-Agenten,",
    "keine abrechenbaren Runner-Minuten und keine menschliche Entwicklungszeit.",
    "Parallele Jobs werden addiert. Die Job-Auswertung umfasst höchstens 40 abgeschlossene",
    "Läufe und höchstens 500 Jobs pro Lauf. Workflow-Läufe werden über höchstens 500",
    "Einträge der letzten sieben Tage abgefragt. Bei Überschreitung ist die Auswertung unvollständig.",
    "Externe Agenten oder ChatGPT-Automationen sind über diese GitHub-API nicht messbar.",
    "",
    "## Letzte Workflow-Läufe",
    "",
    "| Workflow | Ergebnis | Beginn | Link |",
    "|---|---|---|---|",
]
for r in runs[:20]:
    name = str(r["name"]).replace("|", "/")
    report.append(f"| {name} | {r.get('conclusion') or r['status']} | {r['created_at']} | [Lauf]({r['html_url']}) |")
output = "\n".join(report) + "\n"
print(output)
summary = os.environ.get("GITHUB_STEP_SUMMARY")
if summary:
    with open(summary, "a", encoding="utf-8") as handle:
        handle.write(output)
