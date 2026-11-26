#!/usr/bin/env python3
"""Fail closed when workflow Actions or container images use mutable references."""
from __future__ import annotations

import re
import sys
from pathlib import Path

USES_RE = re.compile(r"^\s*(?:-\s*)?uses:\s*(\S+?)(?:\s+#.*)?\s*$")
IMAGE_RE = re.compile(r"^\s*image:\s*(\S+?)(?:\s+#.*)?\s*$")
ACTION_SHA_RE = re.compile(
    r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+(?:/[A-Za-z0-9_.-]+)*@[0-9a-fA-F]{40}$"
)
DOCKER_DIGEST_RE = re.compile(r"^docker://\S+@sha256:[0-9a-fA-F]{64}$")
OCI_DIGEST_RE = re.compile(r"^\S+@sha256:[0-9a-fA-F]{64}$")


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


def find_unpinned_images(text: str, filename: str = "<memory>") -> list[str]:
    """Require every workflow image reference to use an immutable OCI digest."""
    problems: list[str] = []
    for line_number, raw_line in enumerate(text.splitlines(), start=1):
        match = IMAGE_RE.match(raw_line)
        if not match:
            continue
        reference = match.group(1).strip("'\"")
        if OCI_DIGEST_RE.fullmatch(reference):
            continue
        problems.append(
            f"{filename}:{line_number}: container image must be pinned by sha256 digest: {reference}"
        )
    return problems


def find_permission_policy_violations(text: str, filename: str = "<memory>") -> list[str]:
    """Require explicit least-privilege GITHUB_TOKEN permissions per workflow or job."""
    lines = text.splitlines()
    problems: list[str] = []

    def permission_block(index: int, indent: int) -> str:
        first = lines[index].split(":", 1)[1].strip()
        collected = [first] if first else []
        for candidate in lines[index + 1:]:
            if candidate.strip():
                candidate_indent = len(candidate) - len(candidate.lstrip())
                if candidate_indent <= indent:
                    break
            collected.append(candidate.strip())
        return " ".join(collected)

    top_level = next(
        (i for i, line in enumerate(lines) if re.match(r"^permissions\s*:", line)),
        None,
    )
    if top_level is not None:
        block = permission_block(top_level, 0)
        if not block.strip():
            problems.append(f"{filename}:{top_level + 1}: top-level permissions must be explicit")
        if re.search(r"(?i)\bwrite-all\b", block):
            problems.append(f"{filename}:{top_level + 1}: write-all is forbidden; declare only required scopes")
        # Job-level permissions override workflow defaults, so inspect them too.
        for index, line in enumerate(lines):
            if re.match(r"^    permissions\s*:", line):
                job_block = permission_block(index, 4)
                if re.search(r"(?i)\bwrite-all\b", job_block):
                    problems.append(f"{filename}:{index + 1}: job-level write-all permissions are forbidden")
        return problems

    jobs_index = next((i for i, line in enumerate(lines) if line == "jobs:"), None)
    if jobs_index is None:
        return [f"{filename}: workflow has neither top-level permissions nor a jobs section"]

    job_headers = [
        i for i in range(jobs_index + 1, len(lines))
        if re.match(r"^  [A-Za-z0-9_-]+:\s*$", lines[i])
    ]
    if not job_headers:
        return [f"{filename}: jobs section contains no jobs to permission"]

    for position, start in enumerate(job_headers):
        end = job_headers[position + 1] if position + 1 < len(job_headers) else len(lines)
        job_name = lines[start].strip().rstrip(":")
        permission_index = next(
            (i for i in range(start + 1, end) if re.match(r"^    permissions\s*:", lines[i])),
            None,
        )
        if permission_index is None:
            problems.append(f"{filename}:{start + 1}: job '{job_name}' has no explicit permissions")
            continue
        block = permission_block(permission_index, 4)
        if not block.strip():
            problems.append(f"{filename}:{permission_index + 1}: job '{job_name}' permissions must be explicit")
        if re.search(r"(?i)\bwrite-all\b", block):
            problems.append(f"{filename}:{permission_index + 1}: job '{job_name}' uses forbidden write-all permissions")
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
        problems.extend(find_unpinned_images(content, str(path)))
        problems.extend(find_permission_policy_violations(content, str(path)))
    return problems


def main() -> int:
    repository_root = Path(__file__).resolve().parents[1]
    workflow_root = repository_root / ".github" / "workflows"
    problems = audit_workflows(workflow_root)
    if problems:
        print("Workflow supply-chain or token-permission policy violations detected:", file=sys.stderr)
        for problem in problems:
            print(f"- {problem}", file=sys.stderr)
        return 1

    count = sum(
        1 for path in workflow_root.rglob("*")
        if path.is_file() and path.suffix.lower() in {".yml", ".yaml"}
    )
    print(
        f"PASS: external Actions and container images are SHA/digest pinned; explicit least-privilege token permissions are declared in {count} workflow files."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
