# Changelog

Format based on [Keep a Changelog](https://keepachangelog.com/). This file is
honest: it records what actually happened, including bugs found in previously
"released" code.

## [Unreleased] — branch `feature/multi-step-agent`
### Added
- Observe → act → re-observe loop: the agent re-analyzes the page after any
  action that navigates, enabling multi-page flows (search → open result,
  login → cart). `--max-steps` CLI flag (default 3).
- New action verbs: `press`, `select`, `goto`, `scroll`; executor reports
  `navigated` when the URL changes.

## [1.4.1] — 2026-06-10
Professionalization and hardening release. No new product features; this
release makes the existing code verified, packaged and honest.

### Added
- `LICENSE` file (AGPL-3.0). The README claimed AGPL but the file was missing.
- `pyproject.toml`: installable package, `smart-test` and `smart-test-doctor`
  console commands, optional extras matching the defensive imports.
- `--dry-run` mode with a simulated agent: run the full flow (execute →
  persist → history/dashboard/API) without Ollama or Playwright.
- `doctor.py`: environment check (Python, deps, Ollama + models, Playwright
  browsers, database) with clear per-item OK/FAIL.
- Unit test suite: 171 tests on main (from effectively unverified code).
  Measured coverage 66%; tracked honestly in `COVERAGE.md`.
- `requirements-test.txt` and a CI workflow that installs only what the unit
  suite needs and runs it reliably on 3.11/3.12.
- Input validation at the repository boundary (pass_rate range, mode/status
  enums, required url).

### Changed
- Single source of truth for data: CLI, API, dashboard, UI and the CLI entry
  point all read/write the same database (previously four separate JSON
  stores). Repository pattern + injectable engine/session (SOLID).
- Statistics computed in one place (`stats_service`), used by all consumers.
- Heavy stacks (LangChain, Playwright, ChromaDB, influxdb-client) imported
  defensively so every module is importable and testable without them.
- Documentation made truthful: speculative plans labeled as such; fabricated
  metrics ("95% coverage", achieved-looking targets) corrected or reworded.

### Fixed
- **Agent report contract**: the report lacked the keys every consumer read
  (`pass_rate`, `duration`, action counts), so the API stored a hardcoded
  85.0 for every test. Metrics are now computed from the real execution.
- **Streamlit UI never ran**: stray Markdown `---` separators inside the
  Python source caused a `SyntaxError`. Repaired and connected to the
  database.
- **`AdvancedRAG.cluster_domains` crashed on every call** (`len()` of an
  int). Never worked until now.
- Unknown action verbs from the LLM silently distorted pass_rate; they now
  count as failures with a clear error.
- `DetachedInstanceError` on ORM objects after session close; domain tracking
  crash on first insert (`None += 1`); test isolation leaking through a
  module-level engine.

## [1.4] — 2026-06-07
- CLI enhancements (config save/load, history, compare, export, stats) and
  SQLAlchemy database backend (SQLite/PostgreSQL).
- Note: shipped largely unverified; the bugs listed under 1.4.1 were present.

## [1.3] — 2026-06-07
- GitHub Issues integration (auto-create/update/close on failures).

## [1.2] — 2026-06-07
- Email reports (HTML daily report and alerts via SMTP).

## [1.1] — 2026-06-07
- Slack notifications (webhook, color-coded results).

## [1.0] — 2026-06
- Initial platform: agent (Ollama + Playwright), CLI, Streamlit UI, FastAPI,
  RAG/learning modules, Cucumber generation, Grafana/InfluxDB metrics, Docker.
