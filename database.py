"""
Database Module - SQLAlchemy ORM for Smart Test
Supports SQLite (development) and PostgreSQL (production)
"""

from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, ForeignKey, Boolean, Text, Enum as SQLEnum
from sqlalchemy.orm import sessionmaker, relationship, declarative_base
from sqlalchemy.pool import StaticPool
from datetime import datetime, timezone
import os
import logging
from pathlib import Path
import enum

from stats_service import StatsService

logger = logging.getLogger(__name__)


def utcnow():
    """Timezone-aware UTC timestamp (replaces deprecated utcnow)."""
    return datetime.now(timezone.utc)

# ==================== DATABASE CONFIGURATION ====================

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./smarttest.db")
ECHO_SQL = os.getenv("ECHO_SQL", "false").lower() == "true"

Base = declarative_base()


def create_db_engine(database_url: str = DATABASE_URL, echo: bool = ECHO_SQL):
    """Build a SQLAlchemy engine for the given database URL.

    Centralizes engine creation so callers (app, tests) can inject their own
    database instead of depending on a single module-level engine.
    """
    if "postgresql" in database_url:
        return create_engine(database_url, echo=echo)
    # SQLite (development / tests)
    return create_engine(
        database_url,
        echo=echo,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )


def create_session_factory(bound_engine):
    """Build a session factory bound to the given engine."""
    return sessionmaker(autocommit=False, autoflush=False, bind=bound_engine, expire_on_commit=False)


# Default module-level engine and session factory (backwards compatible)
engine = create_db_engine()
SessionLocal = create_session_factory(engine)


# ==================== ENUMS ====================

class TestStatus(str, enum.Enum):
    __test__ = False  # avoid pytest collection
    SUCCESS = "success"
    FAILURE = "failure"
    TIMEOUT = "timeout"
    ERROR = "error"


class TestMode(str, enum.Enum):
    __test__ = False  # avoid pytest collection
    SPEED = "speed"
    BALANCED = "balanced"
    QUALITY = "quality"


# ==================== ORM MODELS ====================

class Test(Base):
    """Test execution record"""
    __test__ = False  # avoid pytest collection
    __tablename__ = "tests"
    
    id = Column(Integer, primary_key=True, index=True)
    url = Column(String(500), index=True)
    objective = Column(String(500))
    pass_rate = Column(Float)
    duration = Column(Float)
    mode = Column(SQLEnum(TestMode), default=TestMode.BALANCED)
    model = Column(String(100), index=True)
    status = Column(SQLEnum(TestStatus), default=TestStatus.SUCCESS)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=utcnow, index=True)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow)
    
    # Relationships
    failures = relationship("Failure", back_populates="test")
    metrics = relationship("Metric", back_populates="test")
    
    def __repr__(self):
        return f"<Test(id={self.id}, url={self.url}, pass_rate={self.pass_rate})>"

    def to_dict(self):
        """Serialize to the dict shape the CLI and exports expect."""
        return {
            "timestamp": self.created_at.isoformat() if self.created_at else "",
            "url": self.url,
            "objective": self.objective,
            "pass_rate": self.pass_rate,
            "duration": self.duration,
            "mode": self.mode.value if self.mode else None,
            "model": self.model,
            "status": self.status.value if self.status else None,
        }


class ModelPerformance(Base):
    """Model performance statistics"""
    __tablename__ = "model_performance"
    
    id = Column(Integer, primary_key=True, index=True)
    model = Column(String(100), unique=True, index=True)
    total_tests = Column(Integer, default=0)
    successful_tests = Column(Integer, default=0)
    avg_pass_rate = Column(Float, default=0.0)
    avg_duration = Column(Float, default=0.0)
    min_pass_rate = Column(Float, default=0.0)
    max_pass_rate = Column(Float, default=0.0)
    created_at = Column(DateTime, default=utcnow)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow)
    
    def __repr__(self):
        return f"<ModelPerformance(model={self.model}, avg_pass_rate={self.avg_pass_rate})>"


class Failure(Base):
    """Test failure tracking"""
    __tablename__ = "failures"
    
    id = Column(Integer, primary_key=True, index=True)
    test_id = Column(Integer, ForeignKey("tests.id"), index=True)
    github_issue_url = Column(String(500), nullable=True)
    slack_notification_sent = Column(Boolean, default=False)
    email_notification_sent = Column(Boolean, default=False)
    resolved = Column(Boolean, default=False)
    resolution_date = Column(DateTime, nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=utcnow)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow)
    
    # Relationships
    test = relationship("Test", back_populates="failures")
    
    def __repr__(self):
        return f"<Failure(id={self.id}, test_id={self.test_id})>"


class Metric(Base):
    """Performance metrics"""
    __tablename__ = "metrics"
    
    id = Column(Integer, primary_key=True, index=True)
    test_id = Column(Integer, ForeignKey("tests.id"), index=True)
    metric_name = Column(String(100), index=True)
    metric_value = Column(Float)
    unit = Column(String(50))
    created_at = Column(DateTime, default=utcnow)
    
    # Relationships
    test = relationship("Test", back_populates="metrics")
    
    def __repr__(self):
        return f"<Metric(name={self.metric_name}, value={self.metric_value})>"


class Domain(Base):
    """Domain tracking"""
    __tablename__ = "domains"
    
    id = Column(Integer, primary_key=True, index=True)
    domain = Column(String(255), unique=True, index=True)
    total_tests = Column(Integer, default=0)
    avg_pass_rate = Column(Float, default=0.0)
    last_tested = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=utcnow)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow)
    
    def __repr__(self):
        return f"<Domain(domain={self.domain}, avg_pass_rate={self.avg_pass_rate})>"


# ==================== DATABASE OPERATIONS ====================

class Database:
    """Facade over the data layer.

    Owns schema/connection management and composes the repositories. The
    public methods are thin delegations kept for backwards compatibility, so
    existing callers and tests keep working while persistence now lives in
    dedicated repositories (Single Responsibility).

    Engine/session can be injected (Dependency Inversion); falls back to the
    module-level defaults.
    """

    def __init__(self, bound_engine=None, session_factory=None):
        self.engine = bound_engine if bound_engine is not None else engine
        if session_factory is not None:
            self.Session = session_factory
        elif bound_engine is not None:
            self.Session = create_session_factory(bound_engine)
        else:
            self.Session = SessionLocal

        # Compose repositories (imported here to avoid an import cycle)
        from repositories import (
            TestRepository,
            ModelPerformanceRepository,
            DomainRepository,
        )
        self.tests = TestRepository(self.Session)
        self.models = ModelPerformanceRepository(self.Session)
        self.domains = DomainRepository(self.Session)

    def get_session(self):
        """Get database session"""
        return self.Session()

    def create_all_tables(self):
        """Create all tables"""
        Base.metadata.create_all(bind=self.engine)
        logger.info("Database tables created")

    def drop_all_tables(self):
        """Drop all tables (WARNING: Development only)"""
        Base.metadata.drop_all(bind=self.engine)
        logger.info("All tables dropped")

    # ---- Delegations (backwards-compatible public API) ----

    def add_test(self, url, objective, pass_rate, duration, mode, model, status="success"):
        return self.tests.add(url, objective, pass_rate, duration, mode, model, status)

    def get_tests(self, limit=100, offset=0):
        return self.tests.list(limit=limit, offset=offset)

    def get_test_by_id(self, test_id):
        return self.tests.get_by_id(test_id)

    def get_tests_by_model(self, model, limit=100):
        return self.tests.get_by_model(model, limit=limit)

    def get_tests_by_url(self, url, limit=100):
        return self.tests.get_by_url(url, limit=limit)

    def update_model_stats(self, model):
        return self.models.refresh(model)

    def get_model_stats(self, model):
        return self.models.get(model)

    def track_domain(self, url):
        return self.domains.track(url)

    def get_statistics(self, days=None):
        return self.tests.statistics(days=days)


# ==================== INITIALIZATION ====================

def init_db():
    """Initialize database"""
    db = Database()
    db.create_all_tables()
    return db


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    db = init_db()
    logger.info("Database initialized")
