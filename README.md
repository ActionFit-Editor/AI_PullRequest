# AI PullRequest (com.actionfit.ai-pr)

ActionFit AI agents use this package to follow the same branch, worktree, commit, pull request, review response, and final reporting workflow across Unity projects.

## Current Scope

This package owns portable AI guidance. Each consuming project still owns its target integration branch, worktree root, Jira status mapping, known Unity blockers, and tool-specific root instructions.

The package does not store GitHub credentials and does not create or publish repositories by itself. AI agents continue to use the locally authenticated `git` and `gh` commands after following the approval and safety rules in `AI_GUIDE.md`.

## Inspect Current Worktrees

Run from the consuming project root to collect local worktree, branch, dirty-state, and target-branch evidence:

```bash
python Packages/com.actionfit.ai-pr/Tools/inspect_worktrees.py
```

Include remote branch and GitHub pull request state:

```bash
python Packages/com.actionfit.ai-pr/Tools/inspect_worktrees.py --remote
```

Use structured output for an AI agent:

```bash
python Packages/com.actionfit.ai-pr/Tools/inspect_worktrees.py --remote --json
```

The inspector is read-only. It does not fetch, prune, reset, delete, merge, push, or change pull requests. Cleanup decisions still require explicit user approval.

## Install

After the package is published, install it through Custom Package Manager or add its Git UPM URL:

```json
{
  "dependencies": {
    "com.actionfit.ai-pr": "https://github.com/ActionFit-Editor/AI_PullRequest.git#1.0.1"
  }
}
```

## Automatic AI Routing

`AI_GUIDE.md` contains a `Requested router entry`. Custom Package Manager scans installed ActionFit package guides and automatically:

1. Adds this package to `Packages/com.actionfit.custompackagemanager/PACKAGE_AI_GUIDE_ROUTER.md`.
2. Refreshes the project's generated `packages/actionfit-packages.md` compatibility pointer.
3. Links the package router from an existing primary `PROJECT.md`, or from a supported root AI entry point when no central project router exists.

This project keeps compatibility pointers under `Docs/AI/workflow/` so older AI entry paths continue to resolve to this package.

## Unity Menu

- Package root: `Tools > Package > AI PullRequest`.
- README: `Tools > Package > AI PullRequest > README`.

## Project Configuration

Projects should keep user-specific values outside the package. Cat Merge Cafe uses ignored `Docs/AI/local-settings.md`:

```md
# Local AI Settings

target_integration_branch: dev_jewoo
worktree_root: .Codex/worktrees
```

Tool-specific files such as `AGENTS.md` and `CLAUDE.md` may define their own worktree root and final report wording, but should always resolve the PR base from the project target integration branch.

## Publishing

Publishing is manual through Custom Package Manager. Creating or editing this embedded package does not create the GitHub repository, push commits, create tags, or append catalog rows.
