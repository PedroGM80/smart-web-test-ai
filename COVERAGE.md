# Test Coverage

Honest, measured snapshot. Regenerate with:

```bash
python -m pytest --cov=. --cov-report=term-missing
```

## Current state

Total: **66%** measured (166 tests passing). Every module now has tests; none
sit at 0%.

| Module | Coverage |
|--------|----------|
| stats_service.py | 100% |
| fake_agent.py | 100% |
| repositories.py | 95% |
| database.py | 91% |
| dashboard_analytics.py | 81% |
| doctor.py | 72% |
| agent.py | 67% |
| cucumber_generator.py | 65% |
| api.py | 62% |
| model_learner.py | 59% |
| advanced_rag.py | 58% |
| rag_optimizer.py | 47% |
| metrics_collector.py | 47% |
| email_reports.py | 45% |
| model_detector.py | 44% |
| cli_enhancements.py | 42% |
| knowledge_base.py | 41% |
| model_selector.py | 39% |
| slack_integration.py | 38% |
| model_benchmarker.py | 38% |
| github_integration.py | 33% |
| smart_test.py | 20% (persist_report + dry-run tested; argparse main not) |

## What is and isn't tested

- **Tested without external services:** all logic that can run without Ollama,
  Playwright, ChromaDB or InfluxDB. Integrations (slack/email/github) use
  mocked HTTP/SMTP; ollama/chromadb/influxdb modules are tested in their
  degraded/no-service paths and their pure helpers; the agent's LLM-response
  parser and action execution are tested with a mocked LLM and page.
- **Not yet tested (needs the real stack):** the live end-to-end run with
  Ollama generating a plan and Playwright driving a real browser. The
  `--dry-run` path exercises the full flow with a simulated agent, but the real
  model/browser path has never been run here.

## Notes

- Earlier docs claimed "95%+ coverage"; that was never measured. This file is
  the source of truth.
- Heavy optional stacks (LangChain, Playwright, influxdb_client, chromadb) are
  imported defensively, so modules load and are testable without them.
- Run `python doctor.py` to check whether a machine has Ollama, the required
  models and the Playwright browsers before attempting a real run.
- Bugs found and fixed while adding tests: agent report contract (placeholder
  pass_rate/duration), AdvancedRAG.cluster_domains (TypeError every call),
  and unknown actions silently distorting pass_rate.
