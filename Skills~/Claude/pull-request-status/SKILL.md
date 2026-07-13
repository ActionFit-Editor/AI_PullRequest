---
name: pull-request-status
description: Inspect the current branch, worktree changes, target branch, and matching pull request state without committing, pushing, creating, or editing anything. Use for PR readiness and overlap checks.
---

# Inspect Pull Request Status

Keep this workflow read-only. Do not fetch, checkout, create branches, acquire worktrees, stage, commit, push, create or edit a PR, transition Jira, or change repository files.

1. Read consuming repository instructions, target integration branch settings, and the AI PullRequest `README.md` and `AI_GUIDE.md`.
2. From the explicitly selected checkout or worktree, inspect:

```bash
git branch --show-current
git status --short --branch
git diff -M -C --name-status
git diff --cached -M -C --name-status
git log -1 --oneline --decorate
```

3. Query GitHub without changing local refs:

```bash
gh pr list --head "<branch>" --state all \
  --json number,state,mergedAt,url,baseRefName,headRefName,title
```

If a PR exists, use read-only `gh pr view` fields and checks as needed. Inspect remote branch existence with read-only remote/API queries rather than mutating local refs.

4. Report the exact worktree path, branch, clean/dirty state, unstaged/staged change inventory, configured target branch, matching PR state and base, and whether the branch is eligible for a new PR or an update.
5. Treat `MERGED` or `CLOSED`, or a user statement that the PR was accepted/applied, as a hard non-reuse result. Flag ambiguous multiple PRs or a base mismatch.

Existing local remote-tracking refs may be stale because this skill does not fetch. Label any ahead/behind inference accordingly. Never turn a readiness report into permission to commit or push.
