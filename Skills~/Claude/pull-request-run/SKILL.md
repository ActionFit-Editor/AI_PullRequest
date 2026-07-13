---
name: pull-request-run
description: Prepare approved changes, validate, commit, push, and create or update a pull request under the consuming repository's workflow. Use only for an explicit PR request.
---

# Run Pull Request Workflow

This is a write-capable workflow. Run only when the user explicitly requests a PR for a defined change scope. The invocation authorizes the normal PR steps for that scope, not unrelated edits, merge, deployment, publication, destructive cleanup, or unapproved sensitive changes.

1. Read the consuming repository instructions, target integration branch, validation rules, Jira rules when applicable, and the package `README.md` and `AI_GUIDE.md`.
2. Fetch and inspect existing branches and all PR states for the task key or domain. Reuse only the canonical eligible branch. Never push to a branch whose PR is merged, closed, accepted, or reported as applied; start a new branch from the latest target branch instead.
3. Use `com.actionfit.ai-worktrees` for physical workspace acquisition unless the user explicitly approved the current checkout. Preserve unrelated dirty files and stop if they cannot be isolated safely.
4. Implement only the approved scope and run proportionate validation. Before staging, compare unstaged, staged, and branch-versus-target changes, inspect ignore-rule and sensitive serialized/configuration changes, and inventory relevant external state. Request explicit approval for any high-risk operation not already named by the user.
5. Stage only intended paths. Commit with title `<branch-name>_<sequence>`, a concise body, no co-author trailer, and the Jira URL as the final body line when the branch starts with an MCC key.
6. Immediately before every push or PR creation, run:

```bash
gh pr list --head "<branch>" --state all \
  --json number,state,mergedAt,url,baseRefName,headRefName
```

Proceed only for no PR or the same still-open PR. A non-fast-forward rejection is branch divergence, not an authentication error; inspect remote history and integrate safely instead of force-pushing.

7. Push normally without force. Create or update the PR against the resolved target integration branch. Write the title and body in Korean, include scope, validation, QA needs, known blockers, Jira URL when applicable, and a separate approved sensitive/destructive inventory.
8. For Jira-backed work, prepend Korean QA notes and transition to the configured internal done state only through the consuming project's approved tools and enabled gates after the PR URL exists. Never move the issue to QA.
9. Report the branch, actual worktree path, PR URL and base, application state, and validation in the exact project-required format. Do not merge, close, delete a branch/worktree, publish, deploy, or change branch protection.
