---
name: pull-request-help
description: Explain AI PullRequest, its installed skills, branch and PR workflow, commit conventions, worktree integration, Jira handoff, menus, and safety boundaries.
---

# AI PullRequest Help

Answer in the user's language. Do not inspect GitHub or change Git, worktrees, pull requests, or Jira unless the user separately requests that operation.

1. Read `PACKAGE_SKILLS.md` first. Treat its generated package identity, complete related-skill table, `$skill-name` invocations, descriptions, and access boundaries as authoritative.
2. Read `Packages/com.actionfit.ai-pr/README.md` and `Packages/com.actionfit.ai-pr/AI_GUIDE.md` when available. Also explain that `com.actionfit.ai-worktrees` owns physical slots, leases, safety checks, and cleanup, while this package owns branch selection, commits, pushes, pull requests, review response, and final reporting.
3. Explain the read-only status skill separately from the explicit write-capable run skill.
4. Summarize the required target-integration-branch resolution, canonical existing branch/PR lookup, accepted-branch non-reuse rule, final scope and sensitive-change audit, `<branch>_<sequence>` commit title, no co-author trailers, Korean PR text, and Jira completion handoff when enabled by the consuming project.
5. List the package README menu under `Tools > Package > AI PullRequest` and refer worktree command help to the installed AI Worktrees package.

State that the package does not store credentials, auto-merge PRs, delete branches/worktrees, publish packages, or bypass project approval and validation rules.
