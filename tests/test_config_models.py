"""Tests for the ``config_models`` module."""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from corpus_cases_medilegal_nz.config_models import (
    FetchConfig,
    HdcPipelineConfig,
    PathsConfig,
    PipelineConfig,
    PipelineDetails,
    ScrapingConfig,
    ValidationConfig,
    load_pipeline_config,
)


@pytest.fixture
def real_config_path() -> Path:
    """Path to the real HDC pipeline YAML config file."""
    repo_root = Path(__file__).resolve().parent.parent
    return repo_root / "config" / "hdc_pipeline.yaml"


class TestLoadPipelineConfig:
    """Tests for ``load_pipeline_config``."""

    def test_loads_real_config(self, real_config_path: Path) -> None:
        """Loading the real YAML file returns a valid PipelineConfig."""
        config = load_pipeline_config(real_config_path)
        assert isinstance(config, PipelineConfig)
        assert config.pipeline.name == "hdc"

    def test_correct_values(self, real_config_path: Path) -> None:
        """Loaded config matches the values in the YAML file."""
        config = load_pipeline_config(real_config_path)
        details = config.pipeline
        assert details.name == "hdc"
        assert details.description == (
            "Health and Disability Commissioner (HDC) NZ Decisions Ingestion Pipeline"
        )
        assert str(details.source_url) == "https://www.hdc.org.nz/decisions/search-decisions/"
        assert str(details.base_url) == "https://www.hdc.org.nz/"
        assert details.paths.raw_dir == Path("data/raw/hdc")
        assert details.paths.processed_dir == Path("data/processed")
        assert details.scraping.page_size == 10
        assert details.scraping.max_pages == 5
        assert details.scraping.timeout == 30
        expected_fields = ["case_id", "date", "title", "commissioner", "citation", "url"]
        assert details.validation.required_metadata_fields == expected_fields

    def test_accepts_str_path(self, real_config_path: Path) -> None:
        """``load_pipeline_config`` also accepts a plain string path."""
        config = load_pipeline_config(str(real_config_path))
        assert isinstance(config, PipelineConfig)

    def test_file_not_found_error(self) -> None:
        """A missing config file raises ``FileNotFoundError``."""
        missing = Path("/nonexistent/path/config.yaml")
        with pytest.raises(FileNotFoundError, match="Configuration file not found"):
            load_pipeline_config(missing)

    def test_invalid_yaml_raises(self, tmp_path: Path) -> None:
        """Invalid YAML content raises a YAML error."""
        bad_file = tmp_path / "bad.yaml"
        bad_file.write_text("{{{invalid: yaml", encoding="utf-8")
        with pytest.raises(yaml.YAMLError):
            load_pipeline_config(bad_file)

    def test_missing_required_field_raises(self, tmp_path: Path) -> None:
        """YAML missing a required field raises a pydantic validation error."""
        incomplete = tmp_path / "incomplete.yaml"
        incomplete.write_text("pipeline:\n  name: hdc\n", encoding="utf-8")
        with pytest.raises(Exception):
            load_pipeline_config(incomplete)


class TestHdcPipelineConfig:
    """Tests for ``HdcPipelineConfig`` default construction."""

    def test_default_construction(self) -> None:
        """Default config creates a valid HDC pipeline config."""
        config = HdcPipelineConfig()
        assert config.pipeline.name == "hdc"
        assert "Health and Disability Commissioner" in config.pipeline.description
        assert str(config.pipeline.source_url) == (
            "https://www.hdc.org.nz/decisions/search-decisions/"
        )
        assert str(config.pipeline.base_url) == "https://www.hdc.org.nz/"

    def test_default_paths(self) -> None:
        """Default paths are set correctly."""
        config = HdcPipelineConfig()
        assert config.pipeline.paths.raw_dir == Path("data/raw/hdc")
        assert config.pipeline.paths.processed_dir == Path("data/processed")

    def test_default_scraping(self) -> None:
        """Default scraping config is set correctly."""
        config = HdcPipelineConfig()
        assert config.pipeline.scraping.page_size == 10
        assert config.pipeline.scraping.max_pages == 5
        assert config.pipeline.scraping.timeout == 30

    def test_default_fetch(self) -> None:
        """Default fetch config is set correctly."""
        config = HdcPipelineConfig()
        assert config.fetch.retry_attempts == 3
        assert config.fetch.retry_backoff_base_seconds == 1.0
        assert config.fetch.rate_limit_per_second == 2.0
        assert config.fetch.request_timeout_seconds == 30

    def test_default_user_agent_fetch(self) -> None:
        """Default user agent in fetch matches expected string."""
        config = HdcPipelineConfig()
        assert "NZ-Medicolegal-Corpus-Sync" in config.fetch.user_agent

    def test_default_validation_metadata_fields(self) -> None:
        """Default required metadata fields are set."""
        config = HdcPipelineConfig()
        expected = ["case_id", "date", "title", "commissioner", "citation", "url"]
        assert config.pipeline.validation.required_metadata_fields == expected

class TestFetchConfig:
    """Tests for ``FetchConfig`` model."""

    def test_default_values(self) -> None:
        """Default construction yields expected values."""
        cfg = FetchConfig()
        assert cfg.retry_attempts == 3
        assert cfg.retry_backoff_base_seconds == 1.0
        assert cfg.rate_limit_per_second == 2.0
        assert cfg.request_timeout_seconds == 30
        assert "NZ-Medicolegal-Corpus-Sync" in cfg.user_agent

    def test_zero_retry_attempts_allowed(self) -> None:
        """retry_attempts=0 is valid (no retries)."""
        cfg = FetchConfig(retry_attempts=0)
        assert cfg.retry_attempts == 0

    def test_custom_values(self) -> None:
        """Custom values override defaults."""
        cfg = FetchConfig(
            retry_attempts=5,
            retry_backoff_base_seconds=2.0,
            rate_limit_per_second=1.0,
            request_timeout_seconds=60,
            user_agent="CustomAgent/1.0",
        )
        assert cfg.retry_attempts == 5
        assert cfg.retry_backoff_base_seconds == 2.0
        assert cfg.rate_limit_per_second == 1.0
        assert cfg.request_timeout_seconds == 60
        assert cfg.user_agent == "CustomAgent/1.0"

    def test_negative_retry_backoff_raises(self) -> None:
        """retry_backoff_base_seconds must be > 0, so -1 should raise."""
        with pytest.raises(Exception):
            FetchConfig(retry_backoff_base_seconds=-1.0)

    def test_zero_rate_limit_raises(self) -> None:
        """rate_limit_per_second must be > 0, so 0 should raise."""
        with pytest.raises(Exception):
            FetchConfig(rate_limit_per_second=0.0)

    def test_negative_timeout_raises(self) -> None:
        """request_timeout_seconds must be > 0."""
        with pytest.raises(Exception):
            FetchConfig(request_timeout_seconds=-5)

    def test_zero_timeout_raises(self) -> None:
        """request_timeout_seconds must be > 0, so 0 should raise."""
        with pytest.raises(Exception):
            FetchConfig(request_timeout_seconds=0)


class TestPathsConfig:
    """Tests for ``PathsConfig`` model."""

    def test_accepts_path_objects(self) -> None:
        """PathsConfig can be constructed with ``Path`` objects."""
        raw = Path("/some/raw")
        processed = Path("/some/processed")
        cfg = PathsConfig(raw_dir=raw, processed_dir=processed)
        assert cfg.raw_dir == raw
        assert cfg.processed_dir == processed

    def test_accepts_strings_as_paths(self) -> None:
        """PathsConfig also accepts strings that get coerced to Path."""
        cfg = PathsConfig(raw_dir="data/raw", processed_dir="data/processed")
        assert cfg.raw_dir == Path("data/raw")
        assert cfg.processed_dir == Path("data/processed")


class TestScrapingConfig:
    """Tests for ``ScrapingConfig`` model."""

    def test_valid_config(self) -> None:
        """Valid scraping config passes validation."""
        cfg = ScrapingConfig(page_size=10, max_pages=5, user_agent="test", timeout=30)
        assert cfg.page_size == 10
        assert cfg.max_pages == 5

    def test_page_size_zero_raises(self) -> None:
        """page_size must be > 0, so 0 should raise."""
        with pytest.raises(Exception):
            ScrapingConfig(page_size=0, max_pages=5, user_agent="test", timeout=30)

    def test_page_size_negative_raises(self) -> None:
        """page_size must be > 0, so negative should raise."""
        with pytest.raises(Exception):
            ScrapingConfig(page_size=-1, max_pages=5, user_agent="test", timeout=30)

    def test_max_pages_zero_raises(self) -> None:
        """max_pages must be > 0, so 0 should raise."""
        with pytest.raises(Exception):
            ScrapingConfig(page_size=10, max_pages=0, user_agent="test", timeout=30)

    def test_timeout_zero_raises(self) -> None:
        """timeout must be > 0."""
        with pytest.raises(Exception):
            ScrapingConfig(page_size=10, max_pages=5, user_agent="test", timeout=0)


class TestPipelineConfig:
    """Tests for ``PipelineConfig`` and ``PipelineDetails``."""

    def test_minimal_pipeline_details(self) -> None:
        """PipelineDetails can be constructed with all required fields."""
        details = PipelineDetails(
            name="test-pipeline",
            description="A test pipeline",
            source_url="https://example.com",
            base_url="https://example.com",
            paths=PathsConfig(raw_dir=Path("raw"), processed_dir=Path("processed")),
            scraping=ScrapingConfig(page_size=10, max_pages=5, user_agent="test", timeout=30),
            validation=ValidationConfig(required_metadata_fields=["id"]),
        )
        assert details.name == "test-pipeline"

    def test_invalid_url_raises(self) -> None:
        """An invalid source_url should raise a validation error."""
        with pytest.raises(Exception):
            PipelineDetails(
                name="test",
                description="desc",
                source_url="not-a-valid-url",
                base_url="https://example.com",
                paths=PathsConfig(raw_dir=Path("raw"), processed_dir=Path("processed")),
                scraping=ScrapingConfig(page_size=10, max_pages=5, user_agent="test", timeout=30),
                validation=ValidationConfig(required_metadata_fields=["id"]),
            )

