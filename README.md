# martins-claude-setup

Setup de Claude Code de Martín: plugins, agentes expertos y el comando `/ship`, para planear, revisar, implementar, hacer QA y mergear con costo controlado.

Funciona en Claude Code, OpenCode y Codex, sobre Windows, Linux y macOS. Para instalarlo en otra máquina, dile a tu agente:

> Lee el AGENTS.md de `martins-claude-setup` y haz el clean install.

## Qué contiene

| Ruta | Para qué sirve |
|---|---|
| `AGENTS.md` | Punto de entrada para cualquier agente. Codex y OpenCode lo leen solos. |
| `CLAUDE.md` | Manda a Claude Code a leer `AGENTS.md`. |
| `INSTALL.md` | La lista de todo lo que hay que instalar y configurar: plugins, ajustes, los 13 agentes (nombre, modelo, prompt) y la verificación. El agente que instala la recorre y crea lo que falta. |
| `install.py` | Instalador idempotente (Windows, Linux, macOS). `--target claude\|opencode\|codex\|all`. Hace respaldo de todo lo que cambia. |
| `models.json` | Modelo de OpenCode Go por nivel (opus, sonnet, haiku). Vacío significa que hereda. |
| `plugins.json` | Marketplaces, plugins globales y plugins opcionales. |
| `claude/commands/ship.md` | El comando `/ship`. Es de los pocos archivos que se copian. |
| `claude/skills/grill-me/` | Skill que entrevista al usuario para cerrar ambigüedades. |
| `docs/PLUGINS.md` | Qué hace cada plugin y cuándo habilitarlo por proyecto. |

## Idea central

Costo bajo con calidad alta se logra con tres decisiones:

1. **Pocos plugins globales.** Cada skill y agente habilitado mete su descripción en el contexto de cada sesión. Los plugins de un lenguaje o de infraestructura se habilitan solo en los repos que los usan (`docs/PLUGINS.md`).
2. **Un modelo por fase.** Opus decide y revisa, Sonnet implementa, Haiku explora.
3. **Un flujo fijo con gates.** Ningún cambio llega al merge sin plan revisado, QA y CI en verde.

## Workflow: `/ship`

`/ship <spec.md | ticket | texto libre>`

Fase 0, entrada y plataforma:
- La tarea puede venir de un `.md` con el spec, de un ticket (GitHub, GitLab, Jira si el conector está autenticado) o de texto libre. Si no puede leer un ticket, lo dice y pide el texto: no inventa su contenido.
- La plataforma de código se detecta con `git remote get-url origin`: GitHub (`gh`), GitLab (`glab`), Bitbucket (`bb` o API REST) y CodeCommit (`aws codecommit`).

Las 5 fases:

1. **Plan.** `explorer` (Haiku) busca en el código. Si la tarea es ambigua, se invoca `grill-me` para decidir con el usuario antes de planear. El plan queda en `docs/plans/<slug>.md` con criterios de aceptación, decisiones, archivos, tests, riesgos y rollback.
2. **Review del plan.** `architect` (Opus) aprueba o pide cambios, máximo 2 rondas. Se suma `system-designer` si cambia un límite entre servicios, y `security` si toca auth, tenancy, secretos o infraestructura.
3. **Implementación.** En un worktree, con un solo experto según el stack, con TDD y un commit por paso lógico.
4. **QA.** `qa-reviewer` y `security`, cada uno en un subagente nuevo. Se corrigen los hallazgos bloqueantes y se repite una vez.
5. **Merge.** PR o MR con la herramienta de la plataforma. Solo se mergea con CI en verde. Si no se puede leer el estado del CI (frecuente en CodeCommit y Bitbucket), el PR queda abierto y se reporta.

Los tickets se mueven de estado solo si existe una herramienta que funcione para ese tracker.

## Agentes

No hay archivos de agentes en el repo: la definición de cada uno está en la sección 5 de `INSTALL.md`, y el agente que instala los crea en el formato de su herramienta. El setup es híbrido: en Claude Code, `architect`, `be-python`, `be-node` y `explorer` se sustituyen por `ecc:architect`, `fastapi-pro` o `python-pro`, `typescript-pro` y el `Explore` integrado, y la fase de QA suma los revisores por lenguaje de ECC. Los otros nueve se crean siempre.

| Modelo | Agentes |
|---|---|
| Opus | `architect`, `system-designer`, `security` |
| Sonnet | `be-java`, `be-go`, `be-node`, `be-python`, `fe-react`, `fe-mobile` (React Native y Flutter), `devops` (Terraform, Ansible, Kubernetes, Docker, CI/CD), `observability` (Prometheus, Grafana, Loki, OpenTelemetry), `qa-reviewer` |
| Haiku | `explorer` |

Los agentes de `devops` solo escriben código y corren `plan`, `validate` y `--check`: nunca `apply`, `destroy` ni deploy. Los agentes `architect`, `system-designer`, `security`, `qa-reviewer` y `explorer` son de solo lectura.

Cada agente nombra en su prompt las skills que debe cargar cuando aplican (por ejemplo `cc-skills-golang:*` para Go o `terraform-skill:terraform-skill` para Terraform). Si ese plugin no está habilitado en el proyecto, el agente trabaja con el conocimiento del modelo.

## Qué no cubre

- No hay skills dedicadas a Ansible ni a Loki: los agentes `devops` y `observability` dependen del modelo y de lo que traiga ECC.
- No hay una skill dedicada a integration testing.
- No se probó `/ship` en CodeCommit ni en Bitbucket. Los comandos de esas plataformas se escribieron de memoria y pueden necesitar ajuste.
- Origen: la lista [awesome-claude-code](https://github.com/hesreallyhim/awesome-claude-code) sirvió de referencia, pero no es una colección de expertos. Los agentes de este repo son propios.

## Mantenimiento

Este repo es la fuente de verdad. Para cambiar un agente, edita su entrada en `INSTALL.md`. Para cambiar `/ship` o `grill-me`, edita el archivo en `claude/` y corre `python install.py --target all --no-plugins` (`python3` en macOS y Linux): los de OpenCode y Codex se generan desde ahí.

## OpenCode y Codex

| Herramienta | Agentes (los crea el agente instalador) | Comando | Skills |
|---|---|---|---|
| OpenCode | `~/.config/opencode/agent/`, como subagentes. Los de solo lectura llevan `write` y `edit` desactivados. | `~/.config/opencode/command/ship.md` | `~/.config/opencode/skill/` |
| Codex | Cada agente como skill con su rol, en `~/.codex/skills/`. No hay modelo por agente. | `~/.codex/prompts/ship.md`, se ejecuta como `/prompts:ship` | `~/.codex/skills/` |

Los nombres `superpowers:*` y `ecc:*` y la herramienta Skill existen solo en Claude Code. El comando generado para las otras herramientas lleva una nota que pide hacer lo mismo a mano. En OpenCode los agentes usan los modelos de OpenCode Go de `models.json`: `kimi-k3.1-pro` para arquitectura y seguridad, `kimi-k2.7-code` para implementar y revisar, `glm-5.3-flash` para explorar. Cada modelo de Go tiene su propio tope mensual y topes de 5 horas y semanales, por eso se reparten entre modelos. Esa asignación es una inferencia por nombre y límite, no por benchmarks. Cámbiala en `models.json`: el agente instalador la lee al crear los agentes.

Los formatos de OpenCode y Codex se escribieron de memoria y no se probaron.
