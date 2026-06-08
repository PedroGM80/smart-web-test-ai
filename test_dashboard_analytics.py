"""
Tests for DashboardAnalytics - verifies it reads test results from the database.
"""

import pytest
from database import Base, create_db_engine, create_session_factory
from repositories import TestRepository
from dashboard_analytics import DashboardAnalytics


@pytest.fixture
def analytics():
    engine = create_db_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    repo = TestRepository(create_session_factory(engine))
    for i in range(3):
        repo.add(
            url=f"https://site{i}.com",
            objective="o",
            pass_rate=80.0 + i * 5,
            duration=20.0 + i,
            mode="balanced",
            model="mistral",
            status="success",
        )
    yield DashboardAnalytics(repository=repo)
    Base.metadata.drop_all(bind=engine)
    engine.dispose()


def test_load_results_from_db(analytics):
    results = analytics.load_results()
    assert len(results) == 3
    assert all("url" in r for r in results)


def test_get_all_data_sections(analytics):
    data = analytics.get_all_data()
    for key in ["summary", "pass_rate_trend", "model_performance",
                "domain_distribution", "mode_distribution", "roi"]:
        assert key in data


def test_summary_reflects_db(analytics):
    data = analytics.get_all_data()
    assert data["summary"]["total_tests"] == 3


def test_empty_database():
    engine = create_db_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    repo = TestRepository(create_session_factory(engine))
    d = DashboardAnalytics(repository=repo)
    assert d.load_results() == []
    engine.dispose()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
