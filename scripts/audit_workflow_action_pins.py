#!/usr/bin/env python3
"""Fail closed when GitHub Actions workflows use mutable external action refs."""
from __future__ import annotations

import re
import sys
from pathlib import Path

USES_RE = re.compile(r"^\s*(?:-\s*)?uses:\s*(\S+?)(?:\s+#.*)?\s*$")
ACTION_SHA_RE = re.compile(
    r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+(?:/[A-Za-z0-9_.-]+)*@[0-9a-fA-F]{40}$"
)
DOCKER_DIGEST_RE = re.compile(r"^docker://\S+@sha256:[0-9a-fA-F]{64}$")


def find_unpinned_actions(text: str, filename: str = "<memory>") -> list[str]:
    """Return one diagnostic per unpinned external action reference."""
    problems: list[str] = []
    for line_number, raw_line in enumerate(text.splitlines(), start=1):
        match = USES_RE.match(raw_line)
        if not match:
            continue

        reference = match.group(1)
        if reference.startswith(("./", "../")):
            continue
        if reference.startswith("docker://"):
            if DOCKER_DIGEST_RE.fullmatch(reference):
                continue
            problems.append(
                f"{filename}:{line_number}: Docker action must be pinned by sha256 digest: {reference}"
            )
            continue
        if ACTION_SHA_RE.fullmatch(reference):
            continue
        problems.append(
            f"{filename}:{line_number}: external action must use a full 40-character commit SHA: {reference}"
        )
    return problems


def audit_workflows(workflow_root: Path) -> list[str]:
    files = sorted(
        path for path in workflow_root.rglob("*")
        if path.is_file() and path.suffix.lower() in {".yml", ".yaml"}
    )
    if not files:
        return [f"No workflow YAML files found under {workflow_root}"]

    problems: list[str] = []
    for path in files:
        try:
            content = path.read_text(encoding="utf-8")
        except (OSError, UnicodeError) as exc:
            problems.append(f"{path}: unable to read workflow: {exc}")
            continue
        problems.extend(find_unpinned_actions(content, str(path)))
    return problems


def main() -> int:
    repository_root = Path(__file__).resolve().parents[1]
    workflow_root = repository_root / ".github" / "workflows"
    problems = audit_workflows(workflow_root)
    if problems:
        print("Unpinned GitHub Actions references detected:", file=sys.stderr)
        for problem in problems:
            print(f"- {problem}", file=sys.stderr)
        return 1

    count = sum(
        1 for path in workflow_root.rglob("*")
        if path.is_file() and path.suffix.lower() in {".yml", ".yaml"}
    )
    print(
        f"PASS: all external Actions in {count} workflow files are immutable SHA/digest pinned."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
