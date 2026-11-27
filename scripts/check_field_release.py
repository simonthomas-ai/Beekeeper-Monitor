#!/usr/bin/env python3
"""Fail-closed evidence gate for real-world VespaGuard deployment.

This is separate from green software CI. No sample data or default approvals.
"""
import ipaddress
import json
import sys
from datetime import date
from pathlib import Path
from urllib.parse import urlparse

EVIDENCE = Path("release/field-acceptance.json")
REQUIRED = {
    "dataset_rights": "Per-image licenses, provenance, reviewed labels and independent splits",
    "model_validation": "Model SHA-256, legal clearance, per-class precision/recall, false alerts and misses",
    "physical_devices": "Real iPhone/Android, camera, offline recovery and station endurance",
    "security_privacy": "Controller, legal basis, notices, retention, deletion, backups and security review",
    "field_pilot": "Independent apiary pilot with documented acceptance and limitations",
}


def valid_evidence_url(value: object) -> bool:
    """Accept only external HTTPS evidence links without embedded secrets."""
    if not isinstance(value, str) or not value or any(char.isspace() for char in value):
        return False
    try:
        parsed = urlparse(value)
        hostname = parsed.hostname
        # Accessing .port also rejects malformed port values.
        _ = parsed.port
    except ValueError:
        return False
    if (
        parsed.scheme.lower() != "https"
        or not hostname
        or parsed.username is not None
        or parsed.password is not None
        or parsed.query
        or parsed.fragment
    ):
        return False

    host = hostname.rstrip(".").lower()
    if (
        host == "localhost"
        or host.endswith((".localhost", ".local", ".internal"))
        or "." not in host and ":" not in host
    ):
        return False
    try:
        address = ipaddress.ip_address(host)
    except ValueError:
        return True
    return address.is_global


def main():
    if not EVIDENCE.is_file():
        print(f"BLOCKED: {EVIDENCE} does not exist. Software CI success is not field approval.")
        return 1
    try:
        payload = json.loads(EVIDENCE.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        print(f"BLOCKED: invalid evidence manifest: {exc}")
        return 1
    if not isinstance(payload, dict):
        print("BLOCKED: evidence manifest root must be a JSON object")
        return 1
    gates = payload.get("gates")
    if not isinstance(gates, dict):
        print("BLOCKED: gates must be an object")
        return 1
    problems = []
    for key, purpose in REQUIRED.items():
        gate = gates.get(key)
        if not isinstance(gate, dict):
            problems.append(f"{key}: missing evidence ({purpose})")
            continue
        url = gate.get("evidence_url")
        reviewer = gate.get("reviewer")
        approved = gate.get("approved") is True
        approved_on = gate.get("approved_on")
        if not approved or not isinstance(reviewer, str) or not reviewer.strip():
            problems.append(f"{key}: explicit reviewer approval missing")
        if not valid_evidence_url(url):
            problems.append(
                f"{key}: evidence_url must be an external HTTPS URL without credentials, query or fragment"
            )
        try:
            approval_date = date.fromisoformat(approved_on)
            if approval_date > date.today():
                problems.append(f"{key}: approval date is in the future")
        except (TypeError, ValueError):
            problems.append(f"{key}: valid ISO approval date missing")
    for problem in problems:
        print("BLOCKED:", problem)
    if problems:
        print("NOT RELEASED: field operation and AI identification are not approved.")
        return 1
    print("EVIDENCE MANIFEST COMPLETE: human verification of linked evidence is still required.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
