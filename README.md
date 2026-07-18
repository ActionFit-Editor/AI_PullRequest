# AI PullRequest (com.actionfit.ai-pr)

ActionFit AI agent가 Unity 프로젝트 전반에서 동일한 branch 선택, commit, pull request, review 대응 및 최종 보고 workflow를 따르도록 하는 패키지입니다.

## 현재 범위

이 패키지는 재사용 가능한 GitHub 협업 가이드를 소유합니다. 재사용 worktree slot, lease, Unity cache 보존, worktree audit과 cleanup dry run은 `com.actionfit.ai-worktrees`가 소유합니다. 사용하는 각 프로젝트는 target integration branch, Jira status mapping과 알려진 Unity blocker를 계속 소유합니다.

패키지는 GitHub 자격 증명을 저장하지 않고 자체적으로 저장소를 생성하거나 publish하지 않습니다. AI agent는 `AI_GUIDE.md`의 승인 및 안전 규칙을 따른 뒤 로컬 인증된 `git`과 `gh` 명령을 사용합니다.

## Worktree 준비 및 점검

이 패키지가 canonical task branch를 선택한 뒤 AI Worktrees로 재사용 slot을 할당합니다.

```bash
python3 Packages/com.actionfit.ai-worktrees/Tools/manage_worktree_slots.py acquire \
  --branch <branch> --base origin/<target-integration-branch> --task <task-id> --json
```

사용하는 프로젝트 root에서 읽기 전용 worktree audit을 실행합니다.

```bash
python3 Packages/com.actionfit.ai-worktrees/Tools/inspect_worktrees.py --remote --json
```

이전 경로는 compatibility wrapper로 유지합니다.

```bash
python3 Packages/com.actionfit.ai-pr/Tools/inspect_worktrees.py --remote --json
```

AI Worktrees는 prune, remove, reset, delete, merge, push 또는 pull request 변경을 실행하지 않습니다. Cleanup 결정에는 계속 명시적 사용자 승인이 필요합니다.

## 설치

패키지가 publish된 후 Custom Package Manager로 설치하거나 Git UPM URL을 추가합니다.

```json
{
  "dependencies": {
    "com.actionfit.ai-pr": "https://github.com/ActionFit-Editor/AI_PullRequest.git#1.0.9"
  }
}
```

## Agent Skill 안내

Custom Package Manager의 `Install or Refresh Agent Skills`는 Codex와 Claude에 다음 project-local skill을 설치합니다.

- `pull-request-help`: branch, commit, PR, worktree 연계와 Jira handoff 규칙을 설명합니다.
- `pull-request-status`: 현재 branch와 matching PR을 read-only로 점검하며 fetch, commit, push, PR 수정을 수행하지 않습니다.
- `pull-request-run`: 사용자가 명시적으로 요청한 범위만 검증·commit·push하고 PR을 생성하거나 열려 있는 동일 PR을 갱신합니다.

write-capable run skill은 암시 호출되지 않으며 merge, branch/worktree 삭제, publish, deploy를 수행하지 않습니다. Refresh는 사용자 수정 및 unmanaged installed skill을 보존합니다.

## 자동 AI Routing

`AI_GUIDE.md`에는 `Requested router entry`가 있습니다. Custom Package Manager가 설치된 ActionFit package guide를 검색하고 자동으로 다음을 수행합니다.

1. 이 패키지를 `Packages/com.actionfit.custompackagemanager/PACKAGE_AI_GUIDE_ROUTER.md`에 추가합니다.
2. 프로젝트에서 생성되는 `packages/actionfit-packages.md` compatibility pointer를 refresh합니다.
3. 기존 primary `PROJECT.md`, 또는 중앙 project router가 없으면 지원되는 root AI entry point에서 package router를 연결합니다.

이 프로젝트는 이전 AI entry 경로도 이 패키지를 해석할 수 있도록 `Docs/AI/workflow/` 아래에 compatibility pointer를 유지합니다.

## Unity 메뉴

- 패키지 root: `Tools > Package > AI PullRequest`
- README: `Tools > Package > AI PullRequest > README`

## 프로젝트 설정

프로젝트는 사용자별 값을 패키지 밖에 보관해야 합니다. Cat Merge Cafe는 Git에서 제외된 `Docs/AI/local-settings.md`를 사용합니다.

```md
# Local AI Settings

target_integration_branch: dev_jewoo
worktree_root: .AI/worktrees
worktree_strategy: pooled
worktree_pool_size: 2
```

`AGENTS.md`, `CLAUDE.md` 같은 root tool 파일은 project router로 연결하는 가벼운 entry point로 유지해야 합니다. Worktree 설정은 Git 제외 local settings, 프로젝트별 PR 보고는 project workflow 문서가 소유합니다.

## 배포

Publish는 Custom Package Manager에서 수동으로 실행합니다. 이 embedded 패키지를 생성하거나 수정해도 GitHub 저장소 생성, commit push, tag 생성 또는 catalog 행 추가가 자동 실행되지 않습니다.
