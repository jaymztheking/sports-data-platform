# CLAUDE.md

## Project

Sports data platform — medallion architecture for NFL, MLB, NBA, NHL analytics. K3s cluster on 6 Raspberry Pis (ARM64). See README.md for full architecture.

## TODO — Story/Test Restructuring (next session)

The roadmap stories and validation tests need restructuring. Core problem:

**Stories like 003 (PostgreSQL Helm Release) say "I want PostgreSQL deployed via Helm on K3s" but the validation tests split into "local file checks" that just verify config files exist and "k3s tests" that check the actual deployment. This is wrong.** The story is about deploying PostgreSQL — a test that checks if `postgres.tf` contains the right strings does NOT validate that story. The story isn't done until PostgreSQL is actually running on K3s.

What needs to happen:
1. **Merge the "write config" and "deploy the thing" concepts.** Story 003 should not be completable by just having the right file contents. The deploy/verify stories (022-024) should not be separate — deployment verification belongs IN each service's story.
2. **Restructure validation tests accordingly.** Remove the false split between "local file checks" and "k3s cluster checks". A story about deploying PostgreSQL should have ONE set of tests, and those tests verify that PostgreSQL is actually deployed and working. File-content checks are at best a precondition, not validation.
3. **Eliminate stories 022-024** (deploy-and-verify-k3s, build-push-arm64-images, verify-deploy-pipeline) as standalone stories. Their acceptance criteria should be folded into the relevant service stories or kept as a single infrastructure prerequisite story.
4. **Re-evaluate what "drafted" means.** Right now 20 stories sit in drafted with passing "local" tests that don't prove anything about the actual user story. These should not be treated as partially validated.

## Conventions

- Package manager: uv
- Linting: ruff + mypy (strict, with third-party ignores)
- Tests: pytest, `tests/unit/` for unit, `tests/validation/` for story acceptance
- IaC: Terraform + Helm in `infra/`
- Custom agents: `.claude/agents/test-writer.md`, `.claude/agents/scrum-master.md`
- Roadmap swim lanes: `roadmap/{planned,active,drafted,validating,blocked,completed}/`
