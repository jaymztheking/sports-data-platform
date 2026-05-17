# CLAUDE.md

## Project

Sports data platform — medallion architecture for NFL, MLB, NBA, NHL analytics. K3s cluster on 6 Raspberry Pis (ARM64). See README.md for full architecture.

## Board State

Stories 002–010 are **infrastructure/deployment** stories: IaC files exist but services have **not been deployed to K3s**. They live in `planned/` and must be completed in numerical order.

Stories 011–021 are **code-writing** stories: modules/DAGs/models are drafted and local tests pass. They live in `drafted/` and will be E2E validated via stories 025–026 once infrastructure is up.

Stories 022–024 have been **deleted** — their acceptance criteria were folded into the relevant service stories (002–010).

### Validation test conventions (enforced)
- Infrastructure stories (002–010): `pytestmark = pytest.mark.k3s` at module level; ONE test class per file; ALL tests verify live cluster state. No file-content checks.
- Code stories (011–021): no k3s marker; tests verify module structure, imports, and logic against real repo modules.
- A story is not moved to `validating/` until its test class passes against the live K3s cluster.

## Conventions

- Package manager: uv
- Linting: ruff + mypy (strict, with third-party ignores)
- Tests: pytest, `tests/unit/` for unit, `tests/validation/` for story acceptance
- IaC: Terraform + Helm in `infra/`
- Custom agents: `.claude/agents/test-writer.md`, `.claude/agents/scrum-master.md`
- Roadmap swim lanes: `roadmap/{planned,active,drafted,validating,blocked,completed}/`
