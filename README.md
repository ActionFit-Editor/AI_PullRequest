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
    "com.actionfit.ai-pr": "https://github.com/ActionFit-Editor/AI_PullRequest.git#1.0.5"
  }
}
```

## Agent Skills

Custom Package Manager의 `Install or Refresh Agent Skills`는 Codex와 Claude에 다음 project-local skill을 설치합니다.

- `pull-request-help`: branch, commit, PR, worktree 연계와 Jira handoff 규칙을 설명합니다.
- `pull-request-status`: 현재 branch와 matching PR을 read-only로 점검하며 fetch, commit, push, PR 수정을 수행하지 않습니다.
- `pull-request-run`: 사용자가 명시적으로 요청한 범위만 검증·commit·push하고 PR을 생성하거나 열려 있는 동일 PR을 갱신합니다.

write-capable run skill은 암시 호출되지 않으며 merge, branch/worktree 삭제, publish, deploy를 수행하지 않습니다. Refresh는 사용자 수정 및 unmanaged installed skill을 보존합니다.

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
