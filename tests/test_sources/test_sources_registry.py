"""Tests for the multi-source registry and base adapter."""
from __future__ import annotations

from pathlib import Path

import pytest

from corpus_cases_medilegal_nz.sources import (
    SOURCE_REGISTRY,
    SourceAdapter,
    get_adapter,
    get_source_ids,
    get_source_info,
)


class TestSourceRegistry:
    """Tests for the SOURCE_REGISTRY dictionary."""

    def test_has_13_sources(self) -> None:
        """Registry must have all 13 sources registered."""
        assert len(SOURCE_REGISTRY) >= 13

    def test_hdc_exists(self) -> None:
        """HDC must be in the registered sources."""
        assert "hdc" in SOURCE_REGISTRY

    def test_all_key_sources_present(self) -> None:
        """All core medical-legal sources must be present."""
        for sid in ["hpdt", "moj_tribunals", "era", "teachers"]:
            assert sid in SOURCE_REGISTRY, f"Missing source: {sid}"

    def test_each_source_has_name(self) -> None:
        """Every source must have a name field."""
        for sid, info in SOURCE_REGISTRY.items():
            assert "name" in info, f"{sid} missing name"
            assert isinstance(info["name"], str)

    def test_each_source_has_config_path(self) -> None:
        """Every source must reference a config file."""
        for sid, info in SOURCE_REGISTRY.items():
            assert "config" in info, f"{sid} missing config"
            config_path = Path(info["config"])
            assert config_path.is_file() or info.get("url", "") == "", (
                f"{sid} config not found: {config_path}"
            )

    def test_get_source_ids_returns_list(self) -> None:
        """get_source_ids() must return all keys."""
        ids = get_source_ids()
        assert len(ids) == len(SOURCE_REGISTRY)
        assert set(ids) == set(SOURCE_REGISTRY.keys())

    def test_get_source_info_returns_dict(self) -> None:
        """get_source_info() must return correct info."""
        info = get_source_info("hdc")
        assert info["name"] == "Health and Disability Commissioner"

    def test_get_source_info_unknown_raises(self) -> None:
        """get_source_info() must raise KeyError for unknown source."""
        with pytest.raises(KeyError):
            get_source_info("nonexistent_source")


class TestSourceAdapter:
    """Tests for the base SourceAdapter class."""

    def test_default_adapter_creation(self) -> None:
        """SourceAdapter must be constructable with source_id and config_path."""
        adapter = SourceAdapter(
            source_id="hdc", config_path=Path("config/hdc_pipeline.yaml")
        )
        assert adapter.source_id == "hdc"

    def test_default_paths(self) -> None:
        """SourceAdapter must set correct default paths."""
        adapter = SourceAdapter(
            source_id="hdc", config_path=Path("config/hdc_pipeline.yaml")
        )
        assert "hdc" in str(adapter.raw_dir)
        assert "processed" in str(adapter.processed_dir)

    def test_fetch_returns_empty(self) -> None:
        """Default fetch() must return empty list."""
        adapter = SourceAdapter(
            source_id="hdc", config_path=Path("config/hdc_pipeline.yaml")
        )
        assert adapter.fetch() == []

    def test_process_passthrough(self) -> None:
        """Default process() must pass through cases unchanged."""
        adapter = SourceAdapter(
            source_id="hdc", config_path=Path("config/hdc_pipeline.yaml")
        )
        cases = [{"case_id": "test"}]
        assert adapter.process(cases) == cases

    def test_validate_default(self) -> None:
        """Default validate() must return True."""
        adapter = SourceAdapter(
            source_id="hdc", config_path=Path("config/hdc_pipeline.yaml")
        )
        assert adapter.validate([]) is True

    def test_get_adapter(self) -> None:
        """get_adapter() must return a SourceAdapter."""
        adapter = get_adapter("hdc")
        assert isinstance(adapter, SourceAdapter)
        assert adapter.source_id == "hdc"
