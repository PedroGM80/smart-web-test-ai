"""
Repositories - data access layer for Smart Test.

Each repository owns CRUD for one entity. This separates persistence from
schema/connection management (which stays in database.Database) and from
business calculations (which live in stats_service.StatsService).

A shared session context manager removes the repeated try/finally that every
operation used to carry.
"""

from contextlib import contextmanager

from stats_service import StatsService
from database import Test, ModelPerformance, Domain, TestStatus, TestMode, utcnow


class BaseRepository:
    """Common session handling for all repositories."""

    def __init__(self, session_factory):
        self._session_factory = session_factory

    @contextmanager
    def _session(self):
        session = self._session_factory()
        try:
            yield session
        finally:
            session.close()


class TestRepository(BaseRepository):
    """CRUD for Test records."""

    __test__ = False  # avoid pytest collection (class name starts with "Test")

    def add(self, url, objective, pass_rate, duration, mode, model, status="success"):
        with self._session() as session:
            test = Test(
                url=url,
                objective=objective,
                pass_rate=pass_rate,
                duration=duration,
                mode=TestMode(mode),
                model=model,
                status=TestStatus(status),
            )
            session.add(test)
            session.commit()
            return test.id

    def list(self, limit=100, offset=0):
        with self._session() as session:
            return session.query(Test).limit(limit).offset(offset).all()

    def get_by_id(self, test_id):
        with self._session() as session:
            return session.query(Test).filter(Test.id == test_id).first()

    def get_by_model(self, model, limit=100):
        with self._session() as session:
            return session.query(Test).filter(Test.model == model).limit(limit).all()

    def get_by_url(self, url, limit=100):
        with self._session() as session:
            return session.query(Test).filter(Test.url == url).limit(limit).all()

    def statistics(self, days=None):
        with self._session() as session:
            query = session.query(Test)
            if days:
                from datetime import timedelta
                cutoff = utcnow() - timedelta(days=days)
                query = query.filter(Test.created_at >= cutoff)
            tests = query.all()
            return StatsService.summarize(
                pass_rates=[t.pass_rate for t in tests],
                durations=[t.duration for t in tests],
                statuses=[t.status.value for t in tests],
            )


class ModelPerformanceRepository(BaseRepository):
    """Aggregated performance metrics per model."""

    def refresh(self, model):
        with self._session() as session:
            tests = session.query(Test).filter(Test.model == model).all()
            if not tests:
                return None

            summary = StatsService.summarize(
                pass_rates=[t.pass_rate for t in tests],
                durations=[t.duration for t in tests],
                statuses=[t.status.value for t in tests],
            )

            perf = session.query(ModelPerformance).filter(
                ModelPerformance.model == model
            ).first()

            if not perf:
                perf = ModelPerformance(model=model)
                session.add(perf)

            perf.total_tests = summary["total_tests"]
            perf.successful_tests = summary["success_count"]
            perf.avg_pass_rate = summary["avg_pass_rate"]
            perf.avg_duration = summary["avg_duration"]
            perf.min_pass_rate = summary["min_pass_rate"]
            perf.max_pass_rate = summary["max_pass_rate"]

            session.commit()
            return perf

    def get(self, model):
        with self._session() as session:
            return session.query(ModelPerformance).filter(
                ModelPerformance.model == model
            ).first()


class DomainRepository(BaseRepository):
    """Domain-level tracking."""

    def track(self, url):
        from urllib.parse import urlparse
        domain = urlparse(url).netloc

        with self._session() as session:
            domain_obj = session.query(Domain).filter(Domain.domain == domain).first()

            if not domain_obj:
                domain_obj = Domain(domain=domain, total_tests=0, avg_pass_rate=0.0)
                session.add(domain_obj)
                session.flush()

            domain_obj.total_tests += 1

            tests = session.query(Test).filter(Test.url.contains(domain)).all()
            if tests:
                domain_obj.avg_pass_rate = sum(t.pass_rate for t in tests) / len(tests)

            domain_obj.last_tested = utcnow()
            session.commit()
            return domain_obj
