# Test Coverage

Honest, measured snapshot. Regenerate with:

```bash
python -m pytest --cov=. --cov-report=term-missing
```

## Current state

Total: **39%** measured (68 tests passing, 1 warning).

### Well covered
| Module | Coverage |
|--------|----------|
| stats_service.py | 100% |
| repositories.py | 95% |
| database.py | 87% |
| dashboard_analytics.py | 81% |
| api.py | 62% |

### Partial
| Module | Coverage |
|--------|----------|
| cli_enhancements.py | 42% |
| agent.py | 40% (report-contract path tested; browser/LLM paths not) |
| model_selector.py | 33% |
| smart_test.py | 22% (persist_report tested; CLI wiring not) |

### Not covered (0%)
These modules have no tests yet. They compile, but their behavior is
unverified. Most depend on external services (Ollama, ChromaDB, InfluxDB,
Slack/GitHub APIs), which is why they were not unit-tested:

advanced_rag, cucumber_generator, email_reports, github_integration,
knowledge_base, metrics_collector, model_benchmarker, model_detector,
model_learner, rag_optimizer, slack_integration.

## Notes

- Earlier project docs claimed "95%+ coverage". That was never measured and is
  not accurate; the real number is tracked here.
- The integration modules (slack/email/github) and the formatting module
  (cucumber_generator) are the most testable of the uncovered set, since their
  logic can be exercised with mocked HTTP/clients.
