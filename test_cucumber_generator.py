"""
Tests for CucumberGenerator - pure Gherkin generation, uses a temp dir.
"""

import pytest
from cucumber_generator import CucumberGenerator


@pytest.fixture
def gen(tmp_path):
    return CucumberGenerator(features_dir=str(tmp_path / "features"))


def test_feature_name_from_url(gen):
    assert gen._generate_feature_name("https://www.github.com/repo") == "Github Testing"


def test_feature_name_strips_scheme_and_tld(gen):
    name = gen._generate_feature_name("http://example.org")
    assert "Example" in name
    assert "http" not in name


def test_generate_feature_contains_gherkin_keywords(gen):
    content = gen.generate_feature(
        url="https://github.com",
        objectives="Test login",
        page_analysis={"elements": []},
        plan="Step 1: open page",
    )
    assert "Feature:" in content
    assert "Background:" in content
    assert "Test login" in content


def test_generate_feature_includes_url(gen):
    content = gen.generate_feature(
        url="https://mysite.com",
        objectives="o",
        page_analysis={},
        plan="p",
    )
    assert "mysite.com" in content


def test_save_feature_writes_file(gen):
    content = "Feature: X"
    path = gen.save_feature("test.feature", content)
    assert path.exists()
    assert path.read_text().startswith("Feature:")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
