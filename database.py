"""
Database Module - SQLAlchemy ORM for Smart Test
Supports SQLite (development) and PostgreSQL (production)
"""

from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, ForeignKey, Boolean, Text, Enum as SQLEnum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.pool import StaticPool
from datetime import datetime
import os
from pathlib import Path
import enum

# ==================== DATABASE CONFIGURATION ====================

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./smarttest.db")
ECHO_SQL = os.getenv("ECHO_SQL", "false").lower() == "true"

# Create engine based on database type
if "postgresql" in DATABASE_URL:
    engine = create_engine(DATABASE_URL, echo=ECHO_SQL)
else:
    # SQLite for development
    engine = create_engine(
        DATABASE_URL,
        echo=ECHO_SQL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, expire_on_commit=False)
Base = declarative_base()


# ==================== ENUMS ====================

class TestStatus(str, enum.Enum):
    SUCCESS = "success"
    FAILURE = "failure"
    TIMEOUT = "timeout"
    ERROR = "error"


class TestMode(str, enum.Enum):
    SPEED = "speed"
    BALANCED = "balanced"
    QUALITY = "quality"


# ==================== ORM MODELS ====================

class Test(Base):
    """Test execution record"""
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
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    failures = relationship("Failure", back_populates="test")
    metrics = relationship("Metric", back_populates="test")
    
    def __repr__(self):
        return f"<Test(id={self.id}, url={self.url}, pass_rate={self.pass_rate})>"


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
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
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
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
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
    created_at = Column(DateTime, default=datetime.utcnow)
    
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
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<Domain(domain={self.domain}, avg_pass_rate={self.avg_pass_rate})>"


# ==================== DATABASE OPERATIONS ====================

class Database:
    """Database operations wrapper"""
    
    def __init__(self):
        self.Session = SessionLocal
    
    def get_session(self):
        """Get database session"""
        return self.Session()
    
    def create_all_tables(self):
        """Create all tables"""
        Base.metadata.create_all(bind=engine)
        print("✅ Database tables created")
    
    def drop_all_tables(self):
        """Drop all tables (WARNING: Development only)"""
        Base.metadata.drop_all(bind=engine)
        print("✅ All tables dropped")
    
    # ==================== TEST OPERATIONS ====================
    
    def add_test(self, url: str, objective: str, pass_rate: float, 
                 duration: float, mode: str, model: str, status: str = "success"):
        """Add test to database"""
        session = self.get_session()
        try:
            test = Test(
                url=url,
                objective=objective,
                pass_rate=pass_rate,
                duration=duration,
                mode=TestMode(mode),
                model=model,
                status=TestStatus(status)
            )
            session.add(test)
            session.commit()
            test_id = test.id
            return test_id
        finally:
            session.close()
    
    def get_tests(self, limit: int = 100, offset: int = 0):
        """Get tests from database"""
        session = self.get_session()
        try:
            tests = session.query(Test).limit(limit).offset(offset).all()
            return tests
        finally:
            session.close()
    
    def get_test_by_id(self, test_id: int):
        """Get test by ID"""
        session = self.get_session()
        try:
            test = session.query(Test).filter(Test.id == test_id).first()
            return test
        finally:
            session.close()
    
    def get_tests_by_model(self, model: str, limit: int = 100):
        """Get tests by model"""
        session = self.get_session()
        try:
            tests = session.query(Test).filter(Test.model == model).limit(limit).all()
            return tests
        finally:
            session.close()
    
    def get_tests_by_url(self, url: str, limit: int = 100):
        """Get tests by URL"""
        session = self.get_session()
        try:
            tests = session.query(Test).filter(Test.url == url).limit(limit).all()
            return tests
        finally:
            session.close()
    
    # ==================== MODEL PERFORMANCE ====================
    
    def update_model_stats(self, model: str):
        """Update model performance statistics"""
        session = self.get_session()
        try:
            tests = session.query(Test).filter(Test.model == model).all()
            
            if not tests:
                return None
            
            total = len(tests)
            successful = sum(1 for t in tests if t.status == TestStatus.SUCCESS)
            avg_pass = sum(t.pass_rate for t in tests) / total
            avg_duration = sum(t.duration for t in tests) / total
            min_pass = min(t.pass_rate for t in tests)
            max_pass = max(t.pass_rate for t in tests)
            
            perf = session.query(ModelPerformance).filter(
                ModelPerformance.model == model
            ).first()
            
            if perf:
                perf.total_tests = total
                perf.successful_tests = successful
                perf.avg_pass_rate = avg_pass
                perf.avg_duration = avg_duration
                perf.min_pass_rate = min_pass
                perf.max_pass_rate = max_pass
            else:
                perf = ModelPerformance(
                    model=model,
                    total_tests=total,
                    successful_tests=successful,
                    avg_pass_rate=avg_pass,
                    avg_duration=avg_duration,
                    min_pass_rate=min_pass,
                    max_pass_rate=max_pass
                )
                session.add(perf)
            
            session.commit()
            return perf
        finally:
            session.close()
    
    def get_model_stats(self, model: str):
        """Get model statistics"""
        session = self.get_session()
        try:
            stats = session.query(ModelPerformance).filter(
                ModelPerformance.model == model
            ).first()
            return stats
        finally:
            session.close()
    
    # ==================== DOMAIN TRACKING ====================
    
    def track_domain(self, url: str):
        """Track domain from URL"""
        from urllib.parse import urlparse
        domain = urlparse(url).netloc
        
        session = self.get_session()
        try:
            domain_obj = session.query(Domain).filter(Domain.domain == domain).first()
            
            if not domain_obj:
                domain_obj = Domain(domain=domain, total_tests=0, avg_pass_rate=0.0)
                session.add(domain_obj)
                session.flush()
            
            domain_obj.total_tests += 1
            
            tests = session.query(Test).filter(Test.url.contains(domain)).all()
            if tests:
                domain_obj.avg_pass_rate = sum(t.pass_rate for t in tests) / len(tests)
            
            domain_obj.last_tested = datetime.utcnow()
            session.commit()
            
            return domain_obj
        finally:
            session.close()
    
    # ==================== REPORTING ====================
    
    def get_statistics(self, days: int = None):
        """Get database statistics"""
        session = self.get_session()
        try:
            query = session.query(Test)
            
            if days:
                from datetime import timedelta
                cutoff = datetime.utcnow() - timedelta(days=days)
                query = query.filter(Test.created_at >= cutoff)
            
            tests = query.all()
            
            if not tests:
                return {
                    "total_tests": 0,
                    "avg_pass_rate": 0,
                    "avg_duration": 0,
                    "success_count": 0,
                    "failure_count": 0
                }
            
            stats = {
                "total_tests": len(tests),
                "avg_pass_rate": sum(t.pass_rate for t in tests) / len(tests),
                "avg_duration": sum(t.duration for t in tests) / len(tests),
                "success_count": sum(1 for t in tests if t.status == TestStatus.SUCCESS),
                "failure_count": sum(1 for t in tests if t.status == TestStatus.FAILURE),
                "min_pass_rate": min(t.pass_rate for t in tests),
                "max_pass_rate": max(t.pass_rate for t in tests)
            }
            return stats
        finally:
            session.close()


# ==================== INITIALIZATION ====================

def init_db():
    """Initialize database"""
    db = Database()
    db.create_all_tables()
    return db


if __name__ == "__main__":
    db = init_db()
    print("✅ Database initialized")
