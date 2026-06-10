"""
Tests for the smart-test utility subcommand dispatcher (run_cli_command).
Previously the whole CLI-enhancements feature was unreachable from the entry
point; these verify the wiring with an injected in-memory repository.
"""

import json
import pytest
from cli_enhancements import CLIEnhancer, run_cli_command, CLI_SUBCOMMANDS
from database import Base, create_db_engine, create_session_factory
from repositories import TestRepository


@pytest.fixture
def cli(tmp_path):
    engine = create_db_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    c = CLIEnhancer(repository=TestRepository(create_session_factory(engine)))
    c.config_dir = tmp_path
    c.cache_dir = tmp_path / "cache"; c.cache_dir.mkdir()
    c.history_add({"url": "https://x.com", "objective": "o", "pass_rate": 90.0,
                   "duration": 10.0, "mode": "balanced", "model": "mistral",
                   "status": "success"})
    return c


def test_subcommand_names_cover_dispatcher():
    assert {"history", "stats", "export", "compare", "config", "clear-cache"} == CLI_SUBCOMMANDS


def test_history_list(cli):
    assert run_cli_command(["history", "list", "--last", "5"], enhancer=cli) == 0


def test_history_clear(cli):
    assert run_cli_command(["history", "clear"], enhancer=cli) == 0
    assert cli._load_history() == []


def test_stats(cli):
    assert run_cli_command(["stats", "--period", "all"], enhancer=cli) == 0


def test_export_json_writes_file(cli, tmp_path):
    out = tmp_path / "r.json"
    assert run_cli_command(["export", "json", str(out)], enhancer=cli) == 0
    assert len(json.loads(out.read_text())) == 1


def test_export_empty_returns_error_code(cli, tmp_path):
    cli.history_clear()
    out = tmp_path / "r.json"
    assert run_cli_command(["export", "json", str(out)], enhancer=cli) == 1


def test_compare(cli):
    cli.history_add({"url": "https://y.com", "objective": "o", "pass_rate": 80.0,
                     "duration": 12.0, "mode": "balanced", "model": "neural-chat",
                     "status": "success"})
    assert run_cli_command(["compare", "mistral", "vs", "neural-chat"], enhancer=cli) == 0


def test_config_load_missing_returns_error(cli):
    assert run_cli_command(["config", "load", "nope"], enhancer=cli) == 1


def test_clear_cache(cli):
    assert run_cli_command(["clear-cache"], enhancer=cli) == 0
