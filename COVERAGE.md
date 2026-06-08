# Test Coverage

Honest, measured snapshot. Regenerate with:

```bash
python -m pytest --cov=. --cov-report=term-missing
```

## Current state

Total: **52%** measured (110 tests passing).

### Covered
| Module | Coverage |
|--------|----------|
| stats_service.py | 100% |
| repositories.py | 95% |
| database.py | 87% |
| dashboard_analytics.py | 81% |
| cucumber_generator.py | 65% |
| api.py | 62% |
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
RAG / model-learning modules, whose logic is coupled to ChromaDB and Ollama
embeddings and is harder to unit-test without those services:

advanced_rag, knowledge_base, model_benchmarker, model_learner, rag_optimizer.

## Notes

- Earlier docs claimed "95%+ coverage"; that was never measured. This file is
  the source of truth.
- Several modules import heavy optional stacks (LangChain, Playwright,
  influxdb_client) defensively, so they can be imported and unit tested
  without those services installed.
- Integration modules (slack/email/github) are tested with mocked HTTP/SMTP.
