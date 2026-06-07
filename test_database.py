"""
Tests for Database Module
"""

import pytest
import tempfile
import os
from pathlib import Path
from database import Database, Test, ModelPerformance, Failure, Domain, TestStatus, TestMode
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


@pytest.fixture
def temp_db():
    """Create isolated in-memory database for each test via dependency injection."""
    from database import Base, create_db_engine, create_session_factory

    test_engine = create_db_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=test_engine)
    session_factory = create_session_factory(test_engine)

    db = Database(bound_engine=test_engine, session_factory=session_factory)
    yield db

    Base.metadata.drop_all(bind=test_engine)
    test_engine.dispose()


class TestDatabase:
    """Database test suite"""
    
    def test_add_test(self, temp_db):
        """Test adding a test to database"""
        test_id = temp_db.add_test(
            url="https://github.com",
            objective="Test repo",
            pass_rate=95.5,
            duration=42.3,
            mode="balanced",
            model="mistral"
        )
        
        assert test_id is not None
        assert isinstance(test_id, int)
    
    def test_get_tests(self, temp_db):
        """Test retrieving tests"""
        # Add tests
        for i in range(3):
            temp_db.add_test(
                url=f"https://example{i}.com",
                objective=f"Test {i}",
                pass_rate=90.0 + i,
                duration=30.0 + i,
                mode="balanced",
                model="mistral"
            )
        
        tests = temp_db.get_tests()
        
        assert len(tests) >= 3
        assert all(t.url.startswith("https://") for t in tests)
    
    def test_get_test_by_id(self, temp_db):
        """Test retrieving test by ID"""
        test_id = temp_db.add_test(
            url="https://github.com",
            objective="Test",
            pass_rate=95.0,
            duration=40.0,
            mode="balanced",
            model="mistral"
        )
        
        test = temp_db.get_test_by_id(test_id)
        
        assert test is not None
        assert test.url == "https://github.com"
        assert test.pass_rate == 95.0
    
    def test_get_tests_by_model(self, temp_db):
        """Test retrieving tests by model"""
        # Add tests with different models
        temp_db.add_test(
            url="https://example.com",
            objective="Test 1",
            pass_rate=90.0,
            duration=30.0,
            mode="balanced",
            model="mistral"
        )
        temp_db.add_test(
            url="https://example.com",
            objective="Test 2",
            pass_rate=85.0,
            duration=35.0,
            mode="balanced",
            model="neural-chat"
        )
        
        mistral_tests = temp_db.get_tests_by_model("mistral")
        
        assert len(mistral_tests) >= 1
        assert all(t.model == "mistral" for t in mistral_tests)
    
    def test_get_tests_by_url(self, temp_db):
        """Test retrieving tests by URL"""
        url = "https://github.com"
        
        for i in range(2):
            temp_db.add_test(
                url=url,
                objective=f"Test {i}",
                pass_rate=90.0 + i,
                duration=30.0 + i,
                mode="balanced",
                model="mistral"
            )
        
        tests = temp_db.get_tests_by_url(url)
        
        assert len(tests) >= 2
        assert all(t.url == url for t in tests)
    
    def test_update_model_stats(self, temp_db):
        """Test updating model statistics"""
        model = "mistral"
        
        # Add multiple tests
        for i in range(5):
            temp_db.add_test(
                url=f"https://example{i}.com",
                objective=f"Test {i}",
                pass_rate=80.0 + i * 4,
                duration=30.0 + i,
                mode="balanced",
                model=model
            )
        
        perf = temp_db.update_model_stats(model)
        
        assert perf is not None
        assert perf.model == model
        assert perf.total_tests >= 5
        assert perf.avg_pass_rate > 0
    
    def test_get_model_stats(self, temp_db):
        """Test retrieving model statistics"""
        model = "neural-chat"
        
        # Add test
        temp_db.add_test(
            url="https://example.com",
            objective="Test",
            pass_rate=92.5,
            duration=35.0,
            mode="balanced",
            model=model
        )
        
        # Update stats
        temp_db.update_model_stats(model)
        
        # Get stats
        stats = temp_db.get_model_stats(model)
        
        assert stats is not None
        assert stats.model == model
        assert stats.total_tests >= 1
    
    def test_track_domain(self, temp_db):
        """Test domain tracking"""
        url = "https://github.com/repo"
        
        domain = temp_db.track_domain(url)
        
        assert domain is not None
        assert domain.domain == "github.com"
    
    def test_get_statistics(self, temp_db):
        """Test getting database statistics"""
        # Add tests
        for i in range(5):
            temp_db.add_test(
                url=f"https://example{i}.com",
                objective=f"Test {i}",
                pass_rate=85.0 + i * 2,
                duration=30.0 + i,
                mode="balanced",
                model="mistral"
            )
        
        stats = temp_db.get_statistics()
        
        assert stats["total_tests"] >= 5
        assert stats["avg_pass_rate"] > 0
        assert stats["avg_duration"] > 0
        assert stats["success_count"] >= 5
    
    def test_statistics_empty_db(self, temp_db):
        """Test statistics with empty database"""
        stats = temp_db.get_statistics()
        
        assert stats["total_tests"] == 0
        assert stats["avg_pass_rate"] == 0
        assert stats["avg_duration"] == 0
    
    def test_full_workflow(self, temp_db):
        """Test complete database workflow"""
        # 1. Add tests
        for i in range(10):
            temp_db.add_test(
                url=f"https://example{i % 3}.com",
                objective=f"Test {i}",
                pass_rate=80.0 + (i % 20),
                duration=30.0 + (i % 10),
                mode="balanced",
                model="mistral" if i % 2 == 0 else "neural-chat"
            )
        
        # 2. Get all tests
        all_tests = temp_db.get_tests(limit=20)
        assert len(all_tests) >= 10
        
        # 3. Get by model
        mistral_tests = temp_db.get_tests_by_model("mistral")
        assert len(mistral_tests) >= 5
        
        # 4. Update model stats
        temp_db.update_model_stats("mistral")
        temp_db.update_model_stats("neural-chat")
        
        # 5. Get statistics
        stats = temp_db.get_statistics()
        assert stats["total_tests"] == 10
        assert stats["avg_pass_rate"] > 0
        assert stats["success_count"] >= 9


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
