"""
Tests for the repository layer (used directly, not via the Database facade).
"""

import pytest
from database import Base, create_db_engine, create_session_factory
from repositories import TestRepository, ModelPerformanceRepository, DomainRepository


@pytest.fixture
def session_factory():
    """Isolated in-memory database per test."""
    engine = create_db_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    yield create_session_factory(engine)
    Base.metadata.drop_all(bind=engine)
    engine.dispose()


class TestTestRepository:

    def test_add_and_get(self, session_factory):
        repo = TestRepository(session_factory)
        test_id = repo.add(
            url="https://github.com",
            objective="Test repo",
            pass_rate=95.0,
            duration=40.0,
            mode="balanced",
            model="mistral",
        )
        fetched = repo.get_by_id(test_id)
        assert fetched is not None
        assert fetched.url == "https://github.com"

    def test_list_and_filter(self, session_factory):
        repo = TestRepository(session_factory)
        repo.add("https://a.com", "T", 90.0, 30.0, "balanced", "mistral")
        repo.add("https://b.com", "T", 80.0, 35.0, "balanced", "neural-chat")

        assert len(repo.list()) == 2
        assert len(repo.get_by_model("mistral")) == 1
        assert len(repo.get_by_url("https://a.com")) == 1

    def test_statistics(self, session_factory):
        repo = TestRepository(session_factory)
        for i in range(3):
            repo.add(f"https://e{i}.com", "T", 80.0 + i * 5, 30.0, "balanced", "mistral")
        stats = repo.statistics()
        assert stats["total_tests"] == 3
        assert stats["avg_pass_rate"] == pytest.approx(85.0)


class TestModelPerformanceRepository:

    def test_refresh_and_get(self, session_factory):
        TestRepository(session_factory).add(
            "https://a.com", "T", 92.0, 30.0, "balanced", "mistral"
        )
        perf_repo = ModelPerformanceRepository(session_factory)
        perf = perf_repo.refresh("mistral")
        assert perf is not None
        assert perf.total_tests == 1
        assert perf_repo.get("mistral").model == "mistral"

    def test_refresh_no_data(self, session_factory):
        perf_repo = ModelPerformanceRepository(session_factory)
        assert perf_repo.refresh("nonexistent") is None


class TestDomainRepository:

    def test_track(self, session_factory):
        domain = DomainRepository(session_factory).track("https://github.com/repo")
        assert domain.domain == "github.com"
        assert domain.total_tests == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
