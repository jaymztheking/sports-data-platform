# CLAUDE.md

> **Start every session by reading `HANDOFF.md`** — it holds the current roadmap state, what's in flight, and the next actions. This file holds the durable rules.

## Project

Sports data platform — medallion architecture for NFL, MLB, NBA, NHL analytics. K3s cluster on 6 Raspberry Pis (ARM64). See README.md for full architecture.

## Board State

**Infrastructure stories** stand: 001–007 completed, 008–009 deployed and in `validating/`, 010 (GitHub Actions) deferred to `backlog/`.

**Pipeline stories (011–025)** are **functional units** — each is one source-to-destination hop in the data pipeline and owns the code, orchestration, and tests needed to prove that hop works:

- 011 MLB pybaseball→Iceberg: tests written, implementation present, local tier green → in `validating/` (awaiting k3s run)
- 012–014 MLB (Iceberg→Postgres, raw→dbt marts, gold→MLflow): **no implementation** — cleared in the teardown; start from tests-first when worked. In `planned/`
- 015–018 NFL, 019–021 NBA, 022–024 NHL: same ingest→load→transform(→ML) pattern, no code yet — `backlog/`
- 025 cross-sport: per-sport schedule marts → unified `fct_daily_schedule` (in `planned/`)

Only code backing a `validating`/`completed`/`active` story exists in the repo. Implementation for `planned`/`backlog` stories is cleared until a live story's tests drive it back in.

**Polish stories (038–042)** in `planned/` are non-pipeline deliverables (sqlfluff, architecture docs, setup guide, README, CI verification) — tackled after the verticals.

### Story model (enforced)
- **Every story has a functional goal confirmed by tests** — never a tests-only story, never an implementation-only story. Implementation and its validation live together.
- A functional unit is **one source → one destination** for a pipeline part (e.g. pybaseball → Iceberg). Do not split a hop's code, orchestration, and tests into separate stories. Do not split sub-layers within one tool/hop (dbt staging+marts is one unit).
- Each story's acceptance criteria group into: **Implementation**, **Validation — unit/structural** (runs locally, no cluster), and **Validation — k3s integration / data contract** (marked `pytest.mark.k3s`, verifies data actually landed at the destination with contract assertions: schema/metadata columns, partition scheme, row counts, not-null keys).
- **The story is the unit of cohesion, not the test file.** A story owns whatever tests prove it works, spread across `tests/unit/`, `tests/integration/`, `tests/validation/` and across as many files as makes sense. No prescribed file/class count — the rule is only that every test belongs to a story and every story is fully proven by its tests. Integration tests carry the `k3s` marker; unit/structural tests do not.
- **TDD: write the tests first.** Starting a story means first writing ALL of its tests — unit/structural, integration, and data-contract — and confirming they cover every acceptance criterion (and fail for the right reason) BEFORE writing implementation. Implementation is done when those tests pass; do not add scope the tests don't demand. All pipeline stories start from no code (implementation for non-active stories is cleared), so pure red-green applies.

### Lifecycle (swim lanes track the next action)
```
planned        spec / ACs only, nothing written
tests_written  tests written first, implementation NOT yet complete
active         currently being worked (WIP)
validating     tests AND implementation both written; local tier green, k3s pending/running
               (bounces back here if k3s fails)
completed      k3s integration passed
blocked        waiting on a dependency/decision
backlog        deferred, not on the near-term radar
```
- **Definition of done:** all non-k3s tests pass locally AND the story's k3s integration tests pass against the live cluster. A story enters `validating/` only when both gates are met (tests + implementation written, local tier green); it reaches `completed/` only after k3s integration passes.

## Conventions

- Package manager: uv
- Linting: ruff + mypy (strict, with third-party ignores)
- Tests: pytest, `tests/unit/` for unit, `tests/validation/` for story acceptance
- IaC: Terraform + Helm in `infra/`
- Custom agents: `.claude/agents/test-writer.md`, `.claude/agents/scrum-master.md`
- Roadmap swim lanes: `roadmap/{backlog,planned,tests_written,active,validating,blocked,completed}/` (see Lifecycle above)
