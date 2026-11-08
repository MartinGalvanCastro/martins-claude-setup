---
description: Plan, review plan, implement in a worktree, QA review, merge. Input: spec .md path, ticket id/URL, or free text. Works on GitHub, GitLab, Bitbucket, CodeCommit.
---

Input: $ARGUMENTS

## 0. Resolve input and platform

Task source, first match wins:
- Path to an existing file (spec, .md): read it. It is the task spec.
- Ticket key or URL: fetch it with the tool that fits. GitHub issue: `gh issue view`. GitLab: `glab issue view`. Jira: Atlassian MCP or ecc:jira, only if authenticated. Other trackers: only if a CLI or MCP for it is available. If none works, say so and ask for the text. Do not guess ticket content.
- Anything else: free text is the task.

If the spec has no acceptance criteria, derive them and put them at the top of the plan.

Code platform: run `git remote get-url origin` and pick:
- `github.com`: PR with `gh pr create`, CI with `gh pr checks`, merge with `gh pr merge`.
- `gitlab`: `glab mr create`, `glab ci status`, `glab mr merge`.
- `bitbucket.org`: `bb` CLI if installed, else REST API with `curl` and a token from the environment. Never print the token.
- `git-codecommit` or `codecommit::`: `aws codecommit create-pull-request`, CI from `aws codepipeline get-pipeline-state` or CodeBuild, merge with `aws codecommit merge-pull-request-by-squash`.
- Unknown host: stop after pushing the branch and tell the user.

Ticket status moves (In Progress, Done) happen only if a working tool exists for that tracker. Otherwise skip and say so in the final report.

## Agents

Use exactly these names. Claude Code uses the middle column. OpenCode and Codex use the right one (local agents).

| Role | Claude Code | OpenCode, Codex |
|---|---|---|
| Explore | built-in `Explore` | `explorer` |
| Plan review | `ecc:architect` | `architect` |
| Python implementation | `api-scaffolding:fastapi-pro` for FastAPI repos, else `python-development:python-pro` | `be-python` |
| Node/TypeScript implementation | `javascript-typescript:typescript-pro` | `be-node` |
| Other implementation | `be-java`, `be-go`, `fe-react`, `fe-mobile`, `devops`, `observability` | same |
| Design, security, QA | `system-designer`, `security`, `qa-reviewer` | same |
| Language review (extra QA) | `ecc:python-reviewer`, `ecc:fastapi-reviewer`, `ecc:typescript-reviewer`, `ecc:java-reviewer`, `ecc:go-reviewer`, `ecc:react-reviewer`, `ecc:flutter-reviewer`, `ecc:database-reviewer` | none, skip |

If an agent name is not available in this session, do not stop. Run that phase with a general-purpose subagent, give it the role and the phase instructions, and name the missing agent in the final report.

## Phases

Stop and report at any failed gate.

1. Plan. Use the Explore agent for lookups. If the task is ambiguous, contradictory, or hides a decision the code and docs cannot settle, invoke the `grill-me` skill (Skill tool) before writing anything, and paste its decision log into the plan. If the task is clear, skip it. Write the plan with superpowers:writing-plans to `docs/plans/<slug>.md`: goal, acceptance criteria, decisions, files touched, tests, risks, rollback.
2. Plan review. Run the Plan review agent, plus `system-designer` if the change adds or alters a service boundary, and `security` if it touches auth, tenancy, secrets or infra. Fix the plan until the Plan review agent approves. Max 2 rounds. If review exposes a decision only the user can make, run `grill-me` again on that point.
3. Implement. Create a worktree (superpowers:using-git-worktrees). Delegate to the one fitting implementation agent from the table. TDD. One commit per logical step.
4. QA. Run `qa-reviewer` and `security` on the diff, each in a fresh subagent. In Claude Code also run the Language review agent for each language touched. Fix blocking findings, then re-run once.
5. Merge. Push, open the PR or MR with the platform's tool, wait for CI, merge only if CI is green. If CI status cannot be read on this platform, do not merge: leave the PR open and report. Never merge on a red check.

Cost rules: Opus only for plan review and security. Sonnet implements and reviews. Haiku explores. Do not paste file contents between agents; pass paths.
