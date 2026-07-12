#!/usr/bin/env python3
"""Collect read-only Git worktree and optional remote pull request evidence."""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def run(command: list[str], cwd: Path, check: bool = True) -> subprocess.CompletedProcess[str]:
    try:
        result = subprocess.run(
            command,
            cwd=str(cwd),
            text=True,
            encoding="utf-8",
            errors="replace",
            capture_output=True,
            timeout=15,
        )
    except subprocess.TimeoutExpired as error:
        result = subprocess.CompletedProcess(
            command,
            124,
            error.stdout or "",
            error.stderr or "command timed out after 15 seconds",
        )
    if check and result.returncode != 0:
        message = result.stderr.strip() or result.stdout.strip() or f"exit {result.returncode}"
        raise RuntimeError(f"{' '.join(command)}: {message}")
    return result


def git(repo: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    return run(["git", *args], repo, check=check)


def resolve_repo(value: str | None) -> Path:
    cwd = Path(value).expanduser().resolve() if value else Path.cwd()
    return Path(git(cwd, "rev-parse", "--show-toplevel").stdout.strip()).resolve()


def read_target_setting(repo: Path) -> str | None:
    settings = repo / "Docs" / "AI" / "local-settings.md"
    if not settings.is_file():
        return None

    pattern = re.compile(r"^\s*target_integration_branch:\s*([^\s#]+)", re.MULTILINE)
    match = pattern.search(settings.read_text(encoding="utf-8", errors="replace"))
    return match.group(1) if match else None


def resolve_target(repo: Path, requested: str | None, warnings: list[str]) -> tuple[str, str]:
    target = requested or read_target_setting(repo)
    if not target:
        target = git(repo, "branch", "--show-current").stdout.strip()
        warnings.append("No configured target was found; using the current branch.")
    if not target:
        raise RuntimeError("The target integration branch could not be determined.")

    for candidate in (target, f"origin/{target}"):
        if git(repo, "rev-parse", "--verify", "--quiet", candidate, check=False).returncode == 0:
            return target, candidate
    raise RuntimeError(f"Target integration branch was not found locally: {target}")


def parse_worktrees(repo: Path) -> list[dict[str, str]]:
    output = git(repo, "worktree", "list", "--porcelain").stdout
    worktrees: list[dict[str, str]] = []
    current: dict[str, str] = {}

    for line in [*output.splitlines(), ""]:
        if not line:
            if current:
                worktrees.append(current)
                current = {}
            continue
        key, _, value = line.partition(" ")
        if key == "branch" and value.startswith("refs/heads/"):
            value = value[len("refs/heads/") :]
        current[key] = value
    return worktrees


def names(repo: Path, *args: str) -> list[str]:
    return [line for line in git(repo, *args).stdout.splitlines() if line]


def is_ancestor(repo: Path, older: str, newer: str) -> bool:
    return git(repo, "merge-base", "--is-ancestor", older, newer, check=False).returncode == 0


def classify(dirty: bool, head_in_target: bool, target_in_head: bool) -> str:
    if dirty:
        return "dirty"
    if head_in_target and target_in_head:
        return "at_target"
    if head_in_target:
        return "integrated_clean"
    if target_in_head:
        return "ahead_clean"
    return "diverged_clean"


def inspect_remote(repo: Path, branch: str, warnings: list[str]) -> dict[str, Any]:
    remote: dict[str, Any] = {"branch_exists": None, "head": None, "pull_requests": []}
    if not branch or branch == "(detached)":
        return remote

    result = git(repo, "ls-remote", "--heads", "origin", f"refs/heads/{branch}", check=False)
    if result.returncode == 0:
        line = result.stdout.strip()
        remote["branch_exists"] = bool(line)
        remote["head"] = line.split()[0] if line else None
    else:
        warnings.append(f"Remote branch inspection failed for {branch}: {result.stderr.strip()}")

    if not shutil.which("gh"):
        warnings.append("GitHub CLI was not found; pull request inspection was skipped.")
        return remote

    fields = "number,title,state,isDraft,headRefName,baseRefName,url,updatedAt,mergedAt"
    result = run(
        ["gh", "pr", "list", "--state", "all", "--head", branch, "--limit", "20", "--json", fields],
        repo,
        check=False,
    )
    if result.returncode != 0:
        warnings.append(f"Pull request inspection failed for {branch}: {result.stderr.strip()}")
        return remote

    try:
        remote["pull_requests"] = json.loads(result.stdout)
    except json.JSONDecodeError as error:
        warnings.append(f"Pull request JSON was invalid for {branch}: {error}")
    return remote


def inspect_worktree(
    repo: Path,
    record: dict[str, str],
    target_ref: str,
    include_remote: bool,
    warnings: list[str],
) -> dict[str, Any]:
    path = Path(record["worktree"]).resolve()
    branch = record.get("branch") or "(detached)"
    head = record.get("HEAD") or git(path, "rev-parse", "HEAD").stdout.strip()

    staged = names(path, "diff", "--cached", "--name-only")
    unstaged = names(path, "diff", "--name-only")
    untracked = names(path, "ls-files", "--others", "--exclude-standard")
    changed = sorted(set(staged) | set(unstaged) | set(untracked))
    dirty = bool(changed)

    counts = git(path, "rev-list", "--left-right", "--count", f"{target_ref}...HEAD").stdout.split()
    target_only, head_only = int(counts[0]), int(counts[1])
    head_in_target = is_ancestor(path, "HEAD", target_ref)
    target_in_head = is_ancestor(path, target_ref, "HEAD")

    commit_lines = git(
        path,
        "log",
        "--max-count=20",
        "--date=iso-strict",
        "--format=%h%x09%ad%x09%s",
        f"{target_ref}..HEAD",
    ).stdout.splitlines()
    unique_commits = []
    for line in commit_lines:
        commit, date, subject = (line.split("\t", 2) + ["", ""])[:3]
        unique_commits.append({"commit": commit, "date": date, "subject": subject})

    result: dict[str, Any] = {
        "path": str(path),
        "is_main_checkout": path == repo,
        "branch": branch,
        "head": head,
        "classification": classify(dirty, head_in_target, target_in_head),
        "dirty": dirty,
        "status": {
            "changed_count": len(changed),
            "staged_count": len(staged),
            "unstaged_count": len(unstaged),
            "untracked_count": len(untracked),
            "changed_files": changed,
        },
        "target_comparison": {
            "target_only_commits": target_only,
            "head_only_commits": head_only,
            "head_in_target": head_in_target,
            "target_in_head": target_in_head,
        },
        "unique_commits": unique_commits,
    }
    if include_remote:
        result["remote"] = inspect_remote(path, branch, warnings)
    return result


def render_text(report: dict[str, Any]) -> str:
    lines = [
        f"Snapshot: {report['snapshot_utc']}",
        f"Repository: {report['repository']}",
        f"Target: {report['target_branch']} ({report['target_ref']})",
        f"Worktrees: {len(report['worktrees'])}",
        "",
    ]
    for item in report["worktrees"]:
        comparison = item["target_comparison"]
        status = item["status"]
        lines.extend(
            [
                f"[{item['classification']}] {item['branch']} @ {item['head'][:12]}",
                f"  path: {item['path']}",
                (
                    f"  changes: {status['changed_count']} "
                    f"(staged {status['staged_count']}, unstaged {status['unstaged_count']}, "
                    f"untracked {status['untracked_count']})"
                ),
                (
                    f"  target: target-only {comparison['target_only_commits']}, "
                    f"head-only {comparison['head_only_commits']}, "
                    f"head-in-target {comparison['head_in_target']}"
                ),
            ]
        )
        if item.get("remote") is not None:
            lines.append(
                f"  remote: branch={item['remote']['branch_exists']}, "
                f"pull_requests={len(item['remote']['pull_requests'])}"
            )
        for commit in item["unique_commits"]:
            lines.append(f"  commit: {commit['commit']} {commit['subject']}")
        lines.append("")

    if report["warnings"]:
        lines.append("Warnings:")
        lines.extend(f"- {warning}" for warning in report["warnings"])
    return "\n".join(lines).rstrip()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", help="Repository path. Defaults to the current Git repository.")
    parser.add_argument("--target", help="Target integration branch.")
    parser.add_argument(
        "--remote",
        action="store_true",
        help="Read remote branch and GitHub PR state without fetching refs.",
    )
    parser.add_argument("--json", action="store_true", help="Print machine-readable JSON.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    warnings: list[str] = []
    try:
        repo = resolve_repo(args.repo)
        target_branch, target_ref = resolve_target(repo, args.target, warnings)
        worktrees = [
            inspect_worktree(repo, record, target_ref, args.remote, warnings)
            for record in parse_worktrees(repo)
        ]
    except (OSError, RuntimeError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 1

    report = {
        "snapshot_utc": datetime.now(timezone.utc).isoformat(),
        "repository": str(repo),
        "target_branch": target_branch,
        "target_ref": target_ref,
        "remote_inspection": args.remote,
        "worktrees": worktrees,
        "warnings": list(dict.fromkeys(warnings)),
    }
    if args.json:
        json.dump(report, sys.stdout, ensure_ascii=True, indent=2)
        sys.stdout.write("\n")
    else:
        print(render_text(report))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
