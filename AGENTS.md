# Repository Guidelines

## Project Structure & Module Organization
- Keep the root clean: `README.md`, `AGENTS.md`, `LICENSE`, and a small `Makefile` or package script entrypoint.  
- Place core source in `src/`; mirror folder names in `tests/` to keep imports predictable.  
- Use `scripts/` for one-off tooling (formatters, linters, release helpers) and `docs/` for design notes or runbooks.  
- Store example payloads or fixtures in `tests/fixtures/` and static assets in `assets/`.  
- If you add services (API, CLI, web), nest them under `src/<service>/` with a clear `index`/`main` entry file and a `README` describing contracts.

## Build, Test, and Development Commands
- Prefer a single entrypoint: add `make setup`, `make dev`, `make test`, `make lint`, and `make fmt` (or equivalent package scripts) so contributors do not need to memorize tool invocations.  
- `make setup`: install dependencies and set up pre-commit hooks.  
- `make dev`: start the local server or watcher; keep it fast and idempotent.  
- `make test`: run the full suite in CI-equivalent mode; allow `FOCUS=<pattern>` overrides for targeted runs.  
- `make lint` / `make fmt`: enforce style; fail on changes that are not formatted.

## Coding Style & Naming Conventions
- Use language-standard formatters (e.g., Prettier for JS/TS, Black/Ruff for Python, gofmt for Go) and run them before pushing.  
- Favor 2-space indentation for JS/TS and 4-space for Python; keep lines ≤100 chars.  
- Naming: packages and directories `kebab-case`; files `kebab-case.ext`; classes `PascalCase`; functions/variables `camelCase`; constants `SCREAMING_SNAKE_CASE`; tests mirror the unit under test (`foo.test.ts`, `bar_test.py`).  
- Keep imports ordered: stdlib, third-party, then local. Avoid unused exports and dead code.

## Testing Guidelines
- Co-locate tests in `tests/` mirroring the `src/` tree; name unit files `*.test.*` and integration `*.spec.*` (or `_test` for Go).  
- Add fixtures in `tests/fixtures/` and prefer deterministic data over random seeds.  
- Target high coverage of domain logic; integration tests should prove wiring, not infrastructure reliability.  
- Run `make test` (or the equivalent package script) before opening a PR; include new tests with every behavior change.

## Commit & Pull Request Guidelines
- Follow Conventional Commits (`feat: add parser skeleton`, `fix: handle empty input`, `chore: bump deps`) to keep history searchable and changelog-friendly.  
- Each commit should be scoped and buildable; avoid mixing refactors with behavior changes.  
- Pull requests: include a short summary, the problem being solved, the approach, and screenshots or sample payloads when UI or API responses change.  
- Link related issues/tickets, list manual verification steps, and call out any follow-up items.

## Security & Configuration Tips
- Never commit secrets; use environment variables and provide a non-sensitive `.env.example`.  
- Add generated files and local caches to `.gitignore`; check in lockfiles for reproducible installs.  
- Document any required system dependencies in `README.md` and keep container/Docker or devcontainer configs updated when dependencies change.  
- Audit third-party packages periodically and pin versions to avoid drift.

## Development Info
- This is an MVP project
- 以尽可能简单高效的方式实现功能，能用进行，后期可能小改
- 项目只有我一个人维护，我对前端不熟，代码中关键的业务逻辑和语法的地方可以加上注释，回答我前端相关的问题的时候也尽可能用我能理解的方式回答，适当说明背景知识、底层细节
- 你可以随意修改本仓库的代码，不需要严格遵循现有的框架，一切以功能正常为准，但要保持代码和仓库整洁
- 尽可能使用中文回复
