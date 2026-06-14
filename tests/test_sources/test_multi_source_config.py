"""Tests for multi-source config loading."""
from __future__ import annotations

from corpus_cases_medilegal_nz.config_models import load_multi_source_config


class TestMultiSourceConfig:
    """Tests for the load_multi_source_config function."""

    def test_load_all_sources(self) -> None:
        """load_multi_source_config() must load all available configs."""
        configs = load_multi_source_config()
        assert len(configs) >= 1
        assert "hdc" in configs

    def test_load_specific_sources(self) -> None:
        """load_multi_source_config() must load only requested sources."""
        configs = load_multi_source_config(source_ids=["hdc"])
        assert len(configs) == 1
        assert "hdc" in configs

    def test_configs_have_pipeline_details(self) -> None:
        """Loaded configs must have pipeline details."""
        configs = load_multi_source_config(source_ids=["hdc"])
        cfg = configs["hdc"]
        assert cfg.pipeline.name == "hdc"
        assert "hdc.org.nz" in str(cfg.pipeline.source_url)

    def test_skip_missing_config_files(self) -> None:
        """load_multi_source_config() must skip missing config files gracefully."""
        configs = load_multi_source_config(source_ids=["nonexistent_source"])
        assert len(configs) == 0
