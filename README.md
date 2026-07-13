# AI PullRequest (com.actionfit.ai-pr)

ActionFit AI agents use this package to follow the same branch selection, commit, pull request, review response, and final reporting workflow across Unity projects.

## Current Scope

This package owns portable GitHub collaboration guidance. `com.actionfit.ai-worktrees` owns reusable worktree slots, leases, Unity cache preservation, worktree audits, and cleanup dry runs. Each consuming project still owns its target integration branch, Jira status mapping, and known Unity blockers.

The package does not store GitHub credentials and does not create or publish repositories by itself. AI agents continue to use the locally authenticated `git` and `gh` commands after following the approval and safety rules in `AI_GUIDE.md`.

## Prepare And Inspect Worktrees

Use AI Worktrees to acquire a reusable slot after this package selects the canonical task branch:

```bash
python3 Packages/com.actionfit.ai-worktrees/Tools/manage_worktree_slots.py acquire \
  --branch <branch> --base origin/<target-integration-branch> --task <task-id> --json
```

Run the read-only worktree audit from the consuming project root:

```bash
python3 Packages/com.actionfit.ai-worktrees/Tools/inspect_worktrees.py --remote --json
```

The previous path remains as a compatibility wrapper:

```bash
python3 Packages/com.actionfit.ai-pr/Tools/inspect_worktrees.py --remote --json
```

AI Worktrees never prunes, removes, resets, deletes, merges, pushes, or changes pull requests. Cleanup decisions still require explicit user approval.

## Install

After the package is published, install it through Custom Package Manager or add its Git UPM URL:

```json
{
  "dependencies": {
    "com.actionfit.ai-pr": "https://github.com/ActionFit-Editor/AI_PullRequest.git#1.0.2"
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
worktree_root: .AI/worktrees
worktree_strategy: pooled
worktree_pool_size: 2
```

Root tool files such as `AGENTS.md` and `CLAUDE.md` should remain lightweight entry points to the project router. Worktree configuration belongs in ignored local settings, and project-specific PR reporting belongs in the project workflow documentation.

## Publishing

Publishing is manual through Custom Package Manager. Creating or editing this embedded package does not create the GitHub repository, push commits, create tags, or append catalog rows.
