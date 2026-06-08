# Test Coverage

Honest, measured snapshot. Regenerate with:

```bash
python -m pytest --cov=. --cov-report=term-missing
```

## Current state

Total: **58%** measured (121 tests passing).

### Covered
| Module | Coverage |
|--------|----------|
| stats_service.py | 100% |
| repositories.py | 95% |
| database.py | 87% |
| dashboard_analytics.py | 81% |
| cucumber_generator.py | 65% |
| api.py | 62% |
| model_learner.py | 59% |
| advanced_rag.py | 58% |
| metrics_collector.py | 47% |
| email_reports.py | 45% |
| model_detector.py | 44% |
| cli_enhancements.py | 42% |
| agent.py | 40% (report-contract path tested; browser/LLM paths not) |
| model_selector.py | 39% |
| slack_integration.py | 38% |
| github_integration.py | 33% |
| smart_test.py | 22% (persist_report tested; CLI wiring not) |

### Not covered (0%)
Core logic is coupled to external services (ChromaDB, Ollama) and belongs in
integration tests, not mocked unit tests:

knowledge_base, model_benchmarker, rag_optimizer.

## Notes

- Earlier docs claimed "95%+ coverage"; that was never measured. This file is
  the source of truth.
- Heavy optional stacks (LangChain, Playwright, influxdb_client) are imported
  defensively, so modules can be imported and unit tested without them.
- Integration modules (slack/email/github) are tested with mocked HTTP/SMTP.
- Two real bugs were found and fixed by adding these tests:
  the agent report contract (placeholder pass_rate/duration) and
  AdvancedRAG.cluster_domains (TypeError on every call).
