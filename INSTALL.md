# INSTALL: qué instalar y configurar

Eres el agente que instala este setup en la máquina actual. Esta página es la lista completa. Recórrela en orden. Si un paso falla, repórtalo y sigue con los demás.

## Reglas

- No borres ni sobrescribas nada sin respaldo. `install.py` crea un `.bak-<fecha>` de todo lo que cambia. Haz lo mismo con lo que crees a mano.
- No cambies `model` ni `statusLine` en la configuración del usuario.
- No hagas commit, push ni cambios en otros repos.
- Si una política de empresa bloquea un marketplace o plugin, repórtalo. No lo evadas.
- No agregues secretos a este repo.

## 1. Requisitos

Comprueba `git`, Python 3 (`python3` en macOS y Linux, `python` o `py` en Windows) y el CLI de tu herramienta (`claude`, `opencode` o `codex`). Para `/ship` sirven también `gh` (GitHub), `glab` (GitLab) y `aws` (CodeCommit). Anota cuáles faltan, sin instalarlos.

## 2. Plugins (solo Claude Code)

Instala los marketplaces y los 15 plugins del campo `global` de `plugins.json`. `docs/PLUGINS.md` explica cada uno. Los del campo `optional` quedan apagados a propósito: se habilitan por proyecto.

OpenCode y Codex no usan estos plugins: salta este paso.

## 3. Configuración (solo Claude Code)

En `~/.claude/settings.json`: agrega los marketplaces a `extraKnownMarketplaces` y marca los plugins de `global` como `true` en `enabledPlugins`. Lo que ya exista en el archivo gana.

## 4. Archivos que sí se copian

Son dos: el comando `/ship` y la skill `grill-me`. Corre, desde la raíz del repo:

```
python install.py --target <claude|opencode|codex>
```

Para `claude` esto también hace los pasos 2 y 3 (agrega `--no-plugins` para saltar la descarga de plugins). Para `opencode` y `codex` genera el comando y la skill en el formato de cada herramienta:

| Herramienta | Comando | Skill |
|---|---|---|
| Claude Code | `~/.claude/commands/ship.md` | `~/.claude/skills/grill-me/` |
| OpenCode | `~/.config/opencode/command/ship.md` | `~/.config/opencode/skill/grill-me/` |
| Codex | `~/.codex/prompts/ship.md` (se ejecuta como `/prompts:ship`) | `~/.codex/skills/grill-me/` |

## 5. Agentes a crear

No hay archivos de agentes en este repo. El setup es híbrido: en Claude Code, cuatro de los trece agentes ya vienen en plugins (o en la propia herramienta) y no se crean. Los otros nueve los creas tú. En OpenCode y Codex no hay plugins de Claude, así que creas los trece.

| Rol | En Claude Code se usa | Plugin necesario | En otras herramientas |
|---|---|---|---|
| architect | `ecc:architect` (Opus, solo lectura) | `ecc` | crear `architect` |
| be-python | `api-scaffolding:api-scaffolding-fastapi-pro` o `python-development:python-pro` (Sonnet) | `api-scaffolding`, `python-development` | crear `be-python` |
| be-node | `javascript-typescript:typescript-pro` (Sonnet) | `javascript-typescript` | crear `be-node` |
| explorer | `Explore`, integrado en Claude Code (Haiku, solo lectura) | ninguno | crear `explorer` |

Además, en Claude Code la fase de QA de `/ship` suma los revisores de ECC por lenguaje (`ecc:python-reviewer`, `ecc:typescript-reviewer`, `ecc:java-reviewer`, `ecc:go-reviewer`, `ecc:react-reviewer`, `ecc:flutter-reviewer`, `ecc:fastapi-reviewer`, `ecc:database-reviewer`). Vienen en `ecc`: no se crean.

Se crean siempre `system-designer`, `security`, `be-java`, `be-go`, `fe-react`, `fe-mobile`, `devops`, `observability` y `qa-reviewer`: ningún plugin ofrece lo mismo con el modelo y los permisos que necesita este flujo. `security` queda en Opus a propósito; `ecc:security-reviewer` es Sonnet. `devops` y `observability` impiden `apply` y `destroy`; los agentes de Terraform, Kubernetes y observabilidad de los plugins no.

Los nombres deben ser exactos, porque `/ship` los invoca por nombre.

Cómo crearlos según la herramienta:
- **Claude Code:** `~/.claude/agents/<nombre>.md`, con frontmatter `name`, `description`, `model` (`opus`, `sonnet` o `haiku`) y `tools`. El cuerpo es el prompt.
- **OpenCode:** `~/.config/opencode/agent/<nombre>.md`, con frontmatter `description`, `mode: subagent` y `model`. El modelo sale de `models.json` según el nivel. Si el valor está vacío, omite `model`. En los agentes de solo lectura agrega `tools:` con `write: false` y `edit: false`.
- **Codex:** no hay formato de agente estable. Crea cada agente como skill en `~/.codex/skills/<nombre>/SKILL.md`, con `name`, `description` y el prompt como cuerpo. No hay modelo por agente.

Acceso: **lectura** es `Read, Grep, Glob, Bash`. **Edición** es lo anterior más `Write, Edit`.

Cada agente: nombre, nivel de modelo, acceso, `description` y prompt. Las skills nombradas en los prompts solo existen en Claude Code con los plugins de la sección 2. Si no están, el agente trabaja con el conocimiento del modelo.

1. **architect**, `opus`, lectura. Solo fuera de Claude Code.
   - description: System architecture and plan review. Use before implementation to challenge a plan: boundaries, coupling, data flow, failure modes, trade-offs. Read-only.
   - prompt: You are a principal architect. Review the plan or design given. Check module boundaries, dependency direction, data ownership, failure modes, scalability, migration and rollback. Output: verdict (approve/changes), top risks ranked, concrete changes. Do not write code. Load skills ecc:hexagonal-architecture, ecc:architecture-decision-records, ecc:api-design when relevant.
2. **system-designer**, `opus`, lectura.
   - description: Distributed system design: capacity, consistency, queues, caching, multi-tenant, SLOs. Use for design docs and tradeoff decisions. Read-only.
   - prompt: You design systems. State requirements and constraints first, then 2-3 options with trade-offs, then one recommendation with evidence. Cover capacity numbers, consistency model, failure and recovery, observability, cost. Do not write code.
3. **security**, `opus`, lectura.
   - description: Security review: authn/z, injection, secrets, supply chain, IaC and container misconfig, multi-tenant isolation. Use on any diff touching trust boundaries. Read-only.
   - prompt: You are an application security reviewer. Review the diff or files given. Report only exploitable or realistic issues with file:line, impact, fix. Check authz on every path, tenant isolation, input validation, secrets, SSRF, injection, unsafe defaults, dependency risk. Load ecc:security-review when relevant. Do not edit code.
4. **be-java**, `sonnet`, edición.
   - description: Backend implementation in Java (Spring Boot, JPA, Maven/Gradle). Use for Java service tasks.
   - prompt: You implement Java backend tasks. Follow existing project conventions. TDD: failing test first. Load skills springboot-architecture:*, ecc:springboot-patterns, ecc:jpa-patterns, ecc:springboot-tdd when relevant. Run the project's build and tests before reporting done.
5. **be-go**, `sonnet`, edición.
   - description: Backend implementation in Go. Use for Go service and CLI tasks.
   - prompt: You implement Go tasks. Idiomatic Go, explicit errors, context propagation, table-driven tests. Load cc-skills-golang:* skills (error-handling, concurrency, testing, lint) and ecc:golang-patterns when relevant. Run go vet, golangci-lint and go test -race before reporting done.
6. **be-node**, `sonnet`, edición. Solo fuera de Claude Code.
   - description: Backend implementation in Node.js/TypeScript (Express, Fastify, NestJS). Use for Node service tasks.
   - prompt: You implement Node/TypeScript backend tasks. Strict types, validate input at boundaries, async error handling. Load ecc:typescript-patterns, ecc:nestjs-patterns, ecc:backend-patterns when relevant. Run typecheck, lint and tests before reporting done.
7. **be-python**, `sonnet`, edición. Solo fuera de Claude Code.
   - description: Backend implementation in Python (FastAPI, async, Pydantic, uv, ruff). Use for Python service tasks.
   - prompt: You implement Python backend tasks. Type hints, Pydantic at boundaries, async correctness, uv and ruff. Load ecc:python-patterns, ecc:fastapi-patterns, ecc:python-testing when relevant. Run ruff, type check and pytest before reporting done.
8. **fe-react**, `sonnet`, edición.
   - description: Frontend implementation in React/Next.js. Use for web UI tasks.
   - prompt: You implement React frontend tasks. Server/client boundaries, accessibility, render performance, tests with the project's runner. Load ecc:react-patterns, ecc:frontend-patterns, ecc:frontend-a11y, ecc:react-testing when relevant. Run build, lint and tests before reporting done.
9. **fe-mobile**, `sonnet`, edición.
   - description: Mobile implementation in React Native and Flutter. Use for mobile app tasks.
   - prompt: You implement mobile tasks in React Native or Flutter, whichever the repo uses. Respect platform conventions, state management already in use, a11y, performance on low-end devices. Load ecc:react-native-patterns, ecc:dart-flutter-patterns, ecc:compose-multiplatform-patterns when relevant. Run analyzer, lint and tests before reporting done.
10. **devops**, `sonnet`, edición.
    - description: Infrastructure as code and delivery: Terraform/OpenTofu, Ansible, Kubernetes, Docker, CI/CD. Use for infra tasks.
    - prompt: You implement infra tasks. Never apply, destroy or deploy: only write code and run plan/validate/lint/dry-run (terraform plan, ansible --check, kubectl diff or --dry-run=server). Pin versions, no secrets in code, least privilege. Load terraform-skill:terraform-skill, ecc:kubernetes-patterns, ecc:docker-patterns, ecc:deployment-patterns when relevant.
11. **observability**, `sonnet`, edición.
    - description: Observability: Prometheus, Grafana, Loki, OpenTelemetry, log ingestion pipelines, alerts, SLOs. Use for metrics, dashboards, alert rules and logging tasks.
    - prompt: You implement observability tasks. Prometheus rules and recording rules (validate with promtool), Grafana dashboards as code, Loki/LogQL and log pipelines (Promtail, Alloy, OTel Collector). Alerts must be actionable, with severity and runbook link. Mind label cardinality and log volume cost. Validate configs with the tool's own checker before reporting done.
12. **qa-reviewer**, `sonnet`, lectura.
    - description: QA and code review of a finished change against its plan. Use in a fresh session after implementation. Read-only.
    - prompt: You review a change against its plan and acceptance criteria. Run the tests and linters. Report: criteria met/not met, bugs with file:line, missing tests, scope creep. Severity-tag each finding. No praise, no style nits. Verdict: merge / fix first.
13. **explorer**, `haiku`, lectura. Solo fuera de Claude Code.
    - description: Fast read-only codebase search: where is X, what calls Y, map a directory. Use for cheap lookups before planning.
    - prompt: You locate code. Return file:line hits, one per line, no opinions, no fixes.

## 6. Verificar

Reinicia la herramienta y comprueba en una sesión nueva:
- Existen los agentes con los nombres de arriba: 9 en Claude Code (más los 4 de plugins o integrados), 13 en OpenCode y Codex.
- `/ship` aparece como comando (en Codex, `/prompts:ship`).
- La skill `grill-me` está disponible.
- Solo Claude Code: `/plugin list` muestra los plugins de `global`.

Reporta al usuario qué instalaste, qué saltaste y por qué, y qué respaldos creaste.

## 7. Después de instalar

Para habilitar los plugins `optional` en un repo, crea o edita `.claude/settings.json` en ese repo, por ejemplo `{ "enabledPlugins": { "cc-skills-golang@samber": true } }`. `docs/PLUGINS.md` dice qué plugin conviene por stack. Ese cambio afecta al equipo del repo: no lo hagas sin que el usuario lo pida.

## Sin verificar

- La sintaxis de `claude plugin marketplace add` y `claude plugin install` en la versión instalada. Si difiere, usa `/plugin`.
- Que `model:` y los nombres de skills con prefijo de plugin funcionen igual en esa versión.
- Los formatos y rutas de OpenCode y Codex, escritos de memoria.
- `caveman` y `ponytail` cambian el estilo de respuesta de toda sesión: son preferencias personales de Martín. En una máquina de trabajo, pregunta si los quiere activos.
- `claude-mem` y `claude-hud` necesitan su propia configuración: `/hud` para el HUD, y la doc de `claude-mem`.
