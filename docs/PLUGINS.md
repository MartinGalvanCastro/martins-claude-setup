# Plugins

La lista exacta y legible por máquina está en `../plugins.json`. Este documento explica el criterio.

## Globales (15, siempre activos)

Son los que sirven en cualquier proyecto.

| Plugin | Para qué |
|---|---|
| `superpowers@claude-plugins-official` | Planear, TDD, worktrees, debugging, review. Es la base de `/ship`. |
| `commit-commands@claude-plugins-official` | Commits y PRs. |
| `code-simplifier@claude-plugins-official` | Simplificar código ya escrito. |
| `claude-md-management@claude-plugins-official` | Mantener `CLAUDE.md`. |
| `claude-code-setup@claude-plugins-official` | Recomendar automatizaciones. |
| `explanatory-output-style@claude-plugins-official` | Estilo de respuesta que explica el porqué. |
| `ecc@ecc` | Reviewers por lenguaje, `e2e-runner`, `security-reviewer`, `database-reviewer` y cientos de skills. Es el plugin que más contexto ocupa. Si el costo sigue alto, es el primer candidato a pasar a nivel de proyecto. |
| `python-development`, `javascript-typescript`, `backend-development`, `api-scaffolding` (`@claude-code-workflows`) | FastAPI, testing de Python y JS, Clean Architecture, Hexagonal, DDD, patrones de API y microservicios. |
| `caveman`, `ponytail` | Respuestas cortas y cambios mínimos. Preferencia personal. |
| `claude-hud`, `claude-mem` | HUD de estado y memoria entre sesiones. |

## Opcionales (se habilitan por proyecto)

Están instalados pero apagados. Habilítalos en `.claude/settings.json` del repo que los use.

| Stack | Plugins |
|---|---|
| Go | `cc-skills-golang@samber` |
| Java | `springboot-architecture@springboot-skills-marketplace`, `jvm-languages@claude-code-workflows` |
| Infra | `terraform-skill@antonbabenko`, `cloud-infrastructure`, `kubernetes-operations`, `cicd-automation`, `deployment-strategies`, `deployment-validation` (`@claude-code-workflows`) |
| Observabilidad | `observability-monitoring`, `application-performance`, `distributed-debugging` (`@claude-code-workflows`) |
| Frontend y móvil | `frontend-mobile-development`, `multi-platform-apps`, `accessibility-compliance` (`@claude-code-workflows`), `playwright@claude-plugins-official` |
| Datos | `supabase@supabase-agent-skills`, `postgres-best-practices@supabase-agent-skills`, `database-design`, `database-migrations` (`@claude-code-workflows`) |
| Seguridad | `security-scanning`, `security-compliance`, `backend-api-security`, `frontend-mobile-security` (`@claude-code-workflows`) |
| Review y testing | `comprehensive-review`, `code-review-ai`, `unit-testing`, `tdd-workflows` (`@claude-code-workflows`), `coderabbit@claude-plugins-official` |
| Plataforma | `vercel@claude-plugins-official` |

El campo `optional` de `plugins.json` también incluye plugins sin relación con este flujo (SEO, blockchain, trading, juegos, RR. HH.). `install.sh` no los instala: están ahí solo como registro de lo que existe en la máquina original.

## Marketplaces

Los 13 repos de origen están en `plugins.json`, campo `marketplaces`. El marketplace `agent-plugins-for-aws` está registrado, pero no hay ningún plugin suyo habilitado.
