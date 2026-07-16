# AI Guide - AI PullRequest

This file is shipped inside the UPM package so an AI assistant in a consuming project can follow a portable development branch and pull request workflow without access to the source project's local AI documentation.

## Package Identity

- Package ID: `com.actionfit.ai-pr`
- Display name: AI PullRequest
- Repository: `https://github.com/ActionFit-Editor/AI_PullRequest.git`
- Current package version at generation time: `1.0.5`
- Unity version: `6000.2`

## Purpose

AI PullRequest defines ActionFit AI guidance for target integration branches, canonical task-branch selection, existing branch and PR discovery, commit messages, PR creation and updates, review response, sensitive-change disclosure, Korean PR text, Jira completion handoff, and final user reports.

`com.actionfit.ai-worktrees` owns physical worktree slots, leases, Unity cache preservation, read-only audits, and cleanup dry runs. A consuming project owns its concrete target branch, Jira mappings, validation blockers, and local workspace settings.

## Agent Skills

- `Skills~/manifest.json` registers schema v2 `pull-request-help`, read-only `pull-request-status`, and explicit write-capable `pull-request-run` for Codex and Claude.
- Help reads the generated `PACKAGE_SKILLS.md` inventory before explaining the package.
- Status does not fetch or change Git/GitHub state. Run is explicit-only and applies this guide's existing branch, commit, PR, sensitive-change, Jira, and final-report contracts without adding merge or cleanup authority.

## Project Router Registration

This package should be listed in `Packages/com.actionfit.custompackagemanager/PACKAGE_AI_GUIDE_ROUTER.md`.

Requested router entry:

- `Packages/com.actionfit.ai-pr/AI_GUIDE.md` - AI PullRequest defines target and task branch selection, commit, PR creation, review response, sensitive-change disclosure, and final reporting rules. Read before selecting or reusing a development branch, pushing a branch, creating or updating a PR, or handling review feedback.

If the router file is not already included in the AI assistant's default reading sequence, the router file is responsible for asking the user to link it from the project's primary AI markdown entry point. Prefer an existing `PROJECT.md` wherever the project keeps it, otherwise use `AGENTS.md`, `CLAUDE.md`, `GEMINI.md`, or another primary AI markdown entry point.

Read this file when:

- selecting or reusing a development branch
- preparing commits for an ActionFit project
- pushing a development branch
- creating, updating, or responding to feedback on a pull request
- deciding whether an accepted or merged PR branch may be reused
- preparing final PR and workspace reports
- changing files under `Packages/com.actionfit.ai-pr/`
- preparing a release for `com.actionfit.ai-pr`

## Resolve Project Settings First

- Read the project's target integration branch before code or project edits, then follow `com.actionfit.ai-worktrees` for local workspace preparation.
- Prefer an ignored local settings file when the project defines one. Never commit user-specific branch, worktree, credential, or account values into this package.
- If the required target integration branch is missing, ask the user which branch to use and create the project-local ignored setting before edits.
- If the user names a different target branch for one task, use it for that task without overwriting the stored default unless requested.
- Do not open normal task PRs directly to `main`. Use the project target integration branch, then create a later integration-branch -> `main` PR only when the project requires it.
- A user's explicit request to edit the current checkout overrides worktree isolation for that task, but does not change the stored default workflow.

## Default Branch And Workspace Flow

Unless the user explicitly requests direct-current-checkout work:

1. Read the project target integration branch.
2. Fetch and search existing branches and PRs for the same Jira key or task domain.
3. Reuse the canonical existing task branch when one exists.
4. Pass the selected branch and latest `origin/<target-integration-branch>` base to `com.actionfit.ai-worktrees`.
5. Acquire a bounded reusable worktree slot, then implement and verify inside that leased slot.
6. Push the task branch and create a PR whose base is the same target integration branch.
7. Release the slot lease only after the workspace is clean and Unity no longer uses it.

Before creating a branch:

```bash
git fetch origin --prune
git branch -a --list '*<ticket-key>*'
gh pr list --search "<ticket-key>" --state all
```

- Treat a full existing branch name containing the ticket key as canonical. Do not create a shortened duplicate.
- Related paired branches may exist; inspect them before deciding whether work belongs on an existing branch.
- Do not acquire or create a worktree for read-only investigation.
- If already inside the intended leased slot, do not reacquire or recreate it.
- Preserve the exact user-provided branch name; avoid helpers that silently add a prefix.

Typical slot acquisition flow:

```bash
git fetch origin
python3 Packages/com.actionfit.ai-worktrees/Tools/manage_worktree_slots.py acquire \
  --branch <branch> \
  --base origin/<target-integration-branch> \
  --task <task-id> \
  --json
```

## Worktree Ownership Boundary

When the user asks what current AI agents or worktrees are doing, use the AI Worktrees inspector:

```bash
python3 Packages/com.actionfit.ai-worktrees/Tools/inspect_worktrees.py --remote --json
```

That package owns audit classifications, slot leases, dirty and Unity-process checks, cleanup dry runs, and the rule that no worktree or branch is deleted without explicit approval. This package may interpret the returned GitHub PR evidence but must not duplicate the physical workspace implementation.

## Commit Rules

- Never add `Co-Authored-By` or any other co-author trailer.
- Commit title format is `<branch-name>_<sequence>` in change order.
- Add a concise 1-3 line body describing what changed.
- When the branch starts with an `MCC-<number>` Jira key, add `Jira: https://actionfit.atlassian.net/browse/<ticket-key>` as the final body line.
- Omit the Jira line when the branch has no Jira key.

Example:

```text
MCC-1330-season-pass-reward-add_1

Add a new costume reward to the season pass tier 50 reward table.

Jira: https://actionfit.atlassian.net/browse/MCC-1330
```

## Required PR State Check

Immediately before every push or PR creation, inspect the current head branch across all PR states:

```bash
gh pr list --head <branch> --state all --json number,state,mergedAt,url,baseRefName,headRefName
```

- No result: a new PR may be created.
- `OPEN`: push only after confirming that it is the same PR currently receiving user feedback.
- `MERGED` or `CLOSED`: never push to that branch. Create a new branch from the latest `origin/<target-integration-branch>`, acquire a safe slot, and open a new PR.
- If the user says the PR was received, merged, accepted, or applied, stop updating the old branch regardless of the API result.
- If a push accidentally reaches a merged PR branch, disclose it immediately, then move the same change to a new branch from the latest target integration branch and create a new PR.

Follow-up work after an accepted PR must contain only the follow-up change on a new branch and PR. Do not make accepted work appear to refresh by adding commits to its old branch.

## Final Scope And Sensitive-Change Audit

Before committing, pushing, or creating a PR, compare the final state with the user's explicitly approved scope:

```bash
git diff -M -C --name-status
git diff --cached -M -C --name-status
git fetch origin <target-integration-branch>
git diff -M -C --name-status origin/<target-integration-branch>...HEAD
```

- Inspect unstaged, staged, and committed branch changes separately.
- Inspect every ignore-rule change and use `git check-ignore -v -- <affected-path>` when tracking behavior may have changed.
- Inspect targeted diffs for scenes, prefabs, ScriptableObjects, serialized YAML, project/build settings, workflows, scripts, package metadata, and credential-related configuration.
- Inventory relevant state outside Git, including runner-local files, home configuration, services, keychains, caches, and copied credentials.
- Stop for explicit approval when a high-risk operation was not named in the approved scope. Do not disguise it as cleanup, hardening, migration, or an implementation detail.

For every approved high-risk change, the PR description and final report must separately name:

- each deleted, moved, replaced, untracked, cleared, or migrated file and field
- each build, CI, release, deploy, signing, credential-source, or gameplay-sequence change and its operational impact
- external paths or systems changed, without secret values
- the exact user-approved operation, verification, reversibility, and rollback or recovery action, including irreversible limits

If an unapproved high-risk change is already committed, pushed, included in a PR, or merged, disclose the affected commit, branch, PR, and integration state. Do not push a correction, revert, close, or modify the PR until the user chooses the recovery action.

## PR Creation And Description

- After implementation and task-appropriate validation are complete, push the branch and create the PR with `gh`.
- Use the resolved target integration branch as the PR base.
- Write PR titles and descriptions in Korean. Preserve code identifiers, file names, commands, log tags, and API names.
- Include a change summary, verification performed, and anything the user or QA must check.
- Include the separate sensitive/destructive inventory when applicable.
- If the branch contains an `MCC-<number>` key, include `Jira: https://actionfit.atlassian.net/browse/<ticket-key>` in the description. Otherwise omit it.
- If validation failed only because of a project-documented known issue, identify that known issue explicitly.
- For AI documentation changes, say whether the project's AI-doc validation was run.

## Jira Completion Handoff

When the work is Jira-backed and the project enables Jira writes:

1. Create the PR and obtain its URL.
2. Prepend Korean QA notes when the project's Jira configuration permits it.
3. Transition the issue to the project's internal `done` mapping before the final report.
4. Leave QA-board movement to the user unless project rules explicitly say otherwise.

If Jira cannot be updated, keep the current state and report the exact blocker, such as missing credentials, dry-run mode, disabled transition permission, missing status mapping, or unavailable transition.

The installed Jira package or project-local Jira compatibility docs own Jira API, credential, description-template, and status-mapping details.

## Review Feedback Loop

- For feedback on the same still-open PR, fix the same branch, re-run proportionate validation, and push; the PR updates automatically.
- Re-run the required PR state check before that push.
- Once the PR is accepted, merged, closed, or reported as applied, use a new branch and PR for every follow-up.

## Final User Report

After code or project file changes, report:

- branch name
- actual work location
- PR URL and target integration branch, or clearly say no PR was created when the user requested direct-current-checkout work
- whether the change exists in the user's current folder or only in an isolated worktree
- the validation performed and any remaining manual Unity validation

When work occurred in an isolated worktree slot, explicitly state that the user's main folder does not contain the change and that the target integration branch must be pulled after the PR is integrated. Use the exact project-specific format when one exists.

Place any approved sensitive/destructive inventory, reversibility, and recovery information immediately before the standard final report.

## Compatibility Boundary

- Existing projects may keep `Docs/AI/workflow/commit.md` and `pull-request.md` as compatibility pointers and project-specific overrides.
- `Docs/AI/workflow/branch-worktree.md` should point to `com.actionfit.ai-worktrees` for physical workspace policy and may retain project-local setting requirements.
- Root `AGENTS.md`, `CLAUDE.md`, or equivalent files should remain lightweight entry points to the project router.
- This package owns portable GitHub collaboration workflow, while `com.actionfit.ai-worktrees` owns portable physical workspace workflow.
- Custom Package Manager owns automatic discovery and registration of this package guide.

## Package Tools Menu

- Unity menu root: `Tools/Package/AI PullRequest/`.
- Keep package commands under this package root.
- `README` opens this package README.
- Do not add README access back to Custom Package Manager package rows or Project Files.

## Release Notes

- Publishing is manual through Custom Package Manager.
- Before reusing a version, check remote Git tags. Published tags are immutable.
- If this package is modified after its version is tagged, bump to the next unused patch version before publishing.
- Do not create repositories, push, tag, or append catalog rows without an explicit user request for publishing.
