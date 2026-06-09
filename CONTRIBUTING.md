# Contributing

Thanks for considering a contribution. This guide reflects how the project
actually works today.

## Quick setup (no AI stack needed)

```bash
git clone https://github.com/PedroGM80/smart-web-test-ai.git
cd smart-web-test-ai
python3 -m venv .venv && source .venv/bin/activate
pip install -e ".[test]"

pytest                    # full unit suite must pass
python doctor.py          # see what your machine has/lacks
python smart_test.py "https://example.com" "Verify load" --dry-run
```

The unit suite runs **without** Ollama, Playwright browsers, ChromaDB or
InfluxDB: heavy stacks are imported defensively and integrations are tested
with mocks. To exercise the real agent, install the extras and browsers:

```bash
pip install -e ".[all]"
playwright install chromium
ollama pull mistral && ollama pull llava
python doctor.py          # everything should be OK before a real run
```

## Ground rules

1. **Tests are required.** New logic ships with tests; bug fixes ship with a
   test that fails without the fix. Run `pytest` before pushing — CI runs the
   same suite on 3.11/3.12 with only `requirements-test.txt` installed, so
   don't add hard imports of the heavy stack to modules the suite touches
   (use the defensive-import pattern you'll see in `agent.py`, `api.py`,
   `metrics_collector.py`).
2. **Honest docs.** Don't claim coverage, metrics or features that aren't
   measured/implemented. `COVERAGE.md` is regenerated from `pytest --cov`,
   not hand-edited upward.
3. **Single source of truth for data.** Test results go through
   `repositories.TestRepository` — never add a new JSON side-store.
4. **Small, descriptive commits.** Explain the why; if you fixed a bug, say
   what was broken.

## Branch & PR flow

- Branch from `develop` (features) or `main` (small fixes/docs):
  `feature/<name>` or `fix/<name>`.
- Open a PR; CI (tests + lint + bandit) must be green.
- Update `CHANGELOG.md` under *Unreleased* for anything user-visible.

## Code style

- Python ≥ 3.9, keep functions small and injectable (see `doctor.py` checks
  or repository session injection for the pattern).
- `flake8` runs in CI: syntax-level errors (E9, F63, F7, F82) fail the build.
- Library code logs (`logging`); `print` is fine only in `__main__` demos and
  CLI output via `rich`.

## Where help is most valuable

- Real-stack verification: running the agent against live sites with Ollama
  and reporting where plans/selectors fail (attach the JSON from `reports/`).
- Integration tests for the ChromaDB/Ollama modules (`knowledge_base`,
  `rag_optimizer`, `model_benchmarker`) with services running.
- The multi-step loop (`feature/multi-step-agent`): retry-with-feedback when
  a selector fails is the next big win.

## Reporting bugs

Open an issue with: command run, expected vs actual, the report JSON if any,
and `python doctor.py` output. Security issues: email the maintainer instead
of opening a public issue.
