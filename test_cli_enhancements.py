"""
Tests for CLI Enhancements
"""

import pytest
import json
import tempfile
from pathlib import Path
from cli_enhancements import CLIEnhancer
from database import Base, create_db_engine, create_session_factory
from repositories import TestRepository


class TestCLIEnhancer:
    """Test suite for CLI enhancements"""
    
    @pytest.fixture
    def cli(self):
        """Create CLI instance with temp dirs and an isolated in-memory repository"""
        test_engine = create_db_engine("sqlite:///:memory:")
        Base.metadata.create_all(bind=test_engine)
        repo = TestRepository(create_session_factory(test_engine))

        with tempfile.TemporaryDirectory() as tmpdir:
            cli = CLIEnhancer(repository=repo)
            cli.config_dir = Path(tmpdir)
            cli.cache_dir = cli.config_dir / "cache"
            cli.cache_dir.mkdir(exist_ok=True)
            yield cli

        Base.metadata.drop_all(bind=test_engine)
        test_engine.dispose()
    
    # ==================== CONFIG TESTS ====================
    
    def test_config_save(self, cli):
        """Test saving configuration"""
        config = {
            "mode": "balanced",
            "model": "mistral",
            "timeout": 30
        }
        
        result = cli.config_save("test-config", config)
        
        assert result is True
        assert (cli.config_dir / "test-config.json").exists()
    
    def test_config_load(self, cli):
        """Test loading configuration"""
        config = {
            "mode": "balanced",
            "model": "mistral"
        }
        
        cli.config_save("test-config", config)
        loaded = cli.config_load("test-config")
        
        assert loaded == config
    
    def test_config_load_nonexistent(self, cli):
        """Test loading nonexistent configuration"""
        loaded = cli.config_load("nonexistent")
        
        assert loaded is None
    
    def test_config_list(self, cli):
        """Test listing configurations"""
        configs = {"mode": "balanced"}
        cli.config_save("config1", configs)
        cli.config_save("config2", configs)
        
        config_files = list(cli.config_dir.glob("*.json"))
        
        assert len(config_files) >= 2
    
    # ==================== HISTORY TESTS ====================
    
    def test_history_add(self, cli):
        """Test adding to history"""
        result = {
            "url": "https://github.com",
            "objective": "Test repo",
            "pass_rate": 95.5,
            "duration": 42.3,
            "mode": "balanced",
            "model": "mistral",
            "status": "success"
        }
        
        cli.history_add(result)
        
        assert len(cli._load_history()) == 1
    
    def test_history_load_and_add(self, cli):
        """Test loading history after adding"""
        result = {
            "url": "https://github.com",
            "pass_rate": 95.5,
            "duration": 42.3,
            "mode": "balanced",
            "model": "mistral",
            "status": "success"
        }
        
        cli.history_add(result)
        history = cli._load_history()
        
        assert len(history) == 1
        assert history[0]["url"] == "https://github.com"
    
    def test_history_multiple_entries(self, cli):
        """Test adding multiple history entries"""
        for i in range(5):
            result = {
                "url": f"https://example{i}.com",
                "pass_rate": 90.0 + i,
                "duration": 30.0 + i,
                "mode": "balanced",
                "model": "mistral",
                "status": "success"
            }
            cli.history_add(result)
        
        history = cli._load_history()
        
        assert len(history) == 5
    
    def test_history_clear(self, cli):
        """Test clearing history"""
        result = {"url": "https://github.com", "pass_rate": 95.0}
        cli.history_add(result)
        
        assert len(cli._load_history()) == 1
        
        cli.history_clear()
        
        assert len(cli._load_history()) == 0
    
    # ==================== COMPARE TESTS ====================
    
    def test_calculate_stats(self, cli):
        """Test statistics calculation"""
        results = [
            {"pass_rate": 90.0, "duration": 30.0},
            {"pass_rate": 95.0, "duration": 35.0},
            {"pass_rate": 85.0, "duration": 25.0}
        ]
        
        stats = cli._calculate_stats(results)
        
        assert stats["count"] == 3
        assert stats["avg_pass_rate"] == pytest.approx(90.0)
        assert stats["avg_duration"] == pytest.approx(30.0)
    
    def test_calculate_stats_empty(self, cli):
        """Test statistics with empty results"""
        stats = cli._calculate_stats([])
        
        assert stats["count"] == 0
        assert stats["avg_pass_rate"] == 0
        assert stats["avg_duration"] == 0
    
    # ==================== EXPORT TESTS ====================
    
    def test_export_csv(self, cli):
        """Test CSV export"""
        # Add some history
        for i in range(3):
            result = {
                "url": f"https://example{i}.com",
                "objective": f"Test {i}",
                "pass_rate": 90.0 + i,
                "duration": 30.0 + i,
                "mode": "balanced",
                "model": "mistral",
                "status": "success"
            }
            cli.history_add(result)
        
        # Export
        csv_file = cli.config_dir / "results.csv"
        result = cli.export_csv(str(csv_file))
        
        assert result is True
        assert csv_file.exists()
    
    def test_export_json(self, cli):
        """Test JSON export"""
        # Add history
        result = {
            "url": "https://github.com",
            "pass_rate": 95.5,
            "duration": 42.3,
            "mode": "balanced",
            "model": "mistral",
            "status": "success"
        }
        cli.history_add(result)
        
        # Export
        json_file = cli.config_dir / "results.json"
        success = cli.export_json(str(json_file))
        
        assert success is True
        assert json_file.exists()
        
        # Verify content
        with open(json_file) as f:
            exported = json.load(f)
            assert len(exported) == 1
            assert exported[0]["url"] == "https://github.com"
    
    def test_export_json_limited(self, cli):
        """Test JSON export with limit"""
        # Add multiple entries
        for i in range(10):
            cli.history_add({
                "url": f"https://example{i}.com",
                "pass_rate": 90.0,
                "duration": 30.0,
                "mode": "balanced",
                "model": "mistral",
                "status": "success"
            })
        
        # Export only last 3
        json_file = cli.config_dir / "results.json"
        cli.export_json(str(json_file), last_n=3)
        
        with open(json_file) as f:
            exported = json.load(f)
            assert len(exported) == 3
    
    def test_export_empty_history(self, cli):
        """Test export with no history"""
        json_file = cli.config_dir / "empty.json"
        result = cli.export_json(str(json_file))
        
        assert result is False
    
    # ==================== CACHE TESTS ====================
    
    def test_clear_cache(self, cli):
        """Test clearing cache"""
        # Create cache file
        cache_file = cli.cache_dir / "test.cache"
        cache_file.write_text("test data")
        
        assert cache_file.exists()
        
        cli.clear_cache()
        
        # Cache dir should be recreated but empty
        assert cli.cache_dir.exists()
        assert not cache_file.exists()
    
    # ==================== INTEGRATION TESTS ====================
    
    def test_full_workflow(self, cli):
        """Test full CLI workflow"""
        # 1. Add test results
        for i in range(5):
            cli.history_add({
                "url": f"https://example{i}.com",
                "objective": f"Test {i}",
                "pass_rate": 85.0 + i * 2,
                "duration": 30.0 + i,
                "mode": "balanced",
                "model": "mistral",
                "status": "success"
            })
        
        # 2. Save config
        config = {"mode": "balanced", "model": "mistral"}
        cli.config_save("workflow-config", config)
        
        # 3. Load config
        loaded = cli.config_load("workflow-config")
        assert loaded == config
        
        # 4. Get stats
        stats = cli._calculate_stats(cli._load_history())
        assert stats["count"] == 5
        
        # 5. Export
        json_file = cli.config_dir / "export.json"
        success = cli.export_json(str(json_file))
        assert success is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
