"""Tests for source-specific adapters."""
from __future__ import annotations

from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

from corpus_cases_medilegal_nz.sources import get_adapter, SourceAdapter
from corpus_cases_medilegal_nz.sources.hdc import HdcSourceAdapter
from corpus_cases_medilegal_nz.sources.hpdt import HpdtSourceAdapter
from corpus_cases_medilegal_nz.sources.moj_tribunals import MojTribunalsSourceAdapter
from corpus_cases_medilegal_nz.sources.era import EraSourceAdapter
from corpus_cases_medilegal_nz.sources.teachers import TeachersSourceAdapter


# ===========================================================================
# HDC
# ===========================================================================

class TestHdcAdapter:
    """Tests for HdcSourceAdapter."""

    def test_imports(self):
        """HdcSourceAdapter is importable."""
        assert HdcSourceAdapter is not None

    def test_extends_base(self):
        """HdcSourceAdapter extends SourceAdapter."""
        assert issubclass(HdcSourceAdapter, SourceAdapter)

    def test_fetch_returns_list(self):
        """fetch() returns a list."""
        adapter = HdcSourceAdapter(source_id="hdc", config_path=Path("config/hdc_pipeline.yaml"))
        result = adapter.fetch()
        assert isinstance(result, list)

    def test_process_sets_source(self):
        """process() sets source field to 'hdc'."""
        adapter = HdcSourceAdapter(source_id="hdc", config_path=Path("config/hdc_pipeline.yaml"))
        cases = [{"case_id": "HDC-001", "text": "test"}]
        result = adapter.process(cases)
        assert result[0]["source"] == "hdc"

    def test_process_sets_metadata(self):
        """process() sets metadata dict on each case."""
        adapter = HdcSourceAdapter(source_id="hdc", config_path=Path("config/hdc_pipeline.yaml"))
        cases = [{"case_id": "HDC-001"}]
        result = adapter.process(cases)
        assert "metadata" in result[0]

    def test_validate_valid(self):
        """validate() returns True for a complete case."""
        adapter = HdcSourceAdapter(source_id="hdc", config_path=Path("config/hdc_pipeline.yaml"))
        case = {
            "case_id": "HDC-001",
            "date": "2024-01-01",
            "title": "Test",
            "commissioner": "A. Commissioner",
            "citation": "[2024]",
            "url": "https://example.com",
        }
        assert adapter.validate([case]) is True

    def test_validate_invalid_missing_fields(self):
        """validate() returns False when required fields are missing."""
        adapter = HdcSourceAdapter(source_id="hdc", config_path=Path("config/hdc_pipeline.yaml"))
        case = {"case_id": "HDC-001"}
        assert adapter.validate([case]) is False

    def test_validate_invalid_empty_case(self):
        """validate() returns False for empty dict."""
        adapter = HdcSourceAdapter(source_id="hdc", config_path=Path("config/hdc_pipeline.yaml"))
        assert adapter.validate([{}]) is False

    def test_validate_multiple_cases(self):
        """validate() checks all cases in the list."""
        adapter = HdcSourceAdapter(source_id="hdc", config_path=Path("config/hdc_pipeline.yaml"))
        valid = {
            "case_id": "HDC-001", "date": "2024-01-01",
            "title": "T", "commissioner": "C",
            "citation": "[2024]", "url": "https://ex.com",
        }
        invalid = {"case_id": "HDC-002"}
        assert adapter.validate([valid]) is True
        assert adapter.validate([valid, invalid]) is False

    def test_fetch_mocked(self):
        """fetch() reads source_url from config (mocked)."""
        adapter = HdcSourceAdapter(source_id="hdc", config_path=Path("config/hdc_pipeline.yaml"))
        with patch("corpus_cases_medilegal_nz.sources.hdc.load_pipeline_config") as mock_load:
            with patch("corpus_cases_medilegal_nz.sources.hdc.HdcFetcher") as mock_cls:
                mock_cfg = MagicMock()
                mock_cfg.pipeline.source_url = "https://www.hdc.org.nz/decisions/"
                mock_load.return_value = mock_cfg

                mock_fetcher = MagicMock()
                mock_fetcher.__enter__.return_value = mock_fetcher
                mock_fetcher.fetch_url.return_value = MagicMock(text="<html>stub</html>")
                mock_cls.return_value = mock_fetcher

                result = adapter.fetch()

                mock_cls.assert_called_once()
                mock_fetcher.fetch_url.assert_called_once_with("https://www.hdc.org.nz/decisions/")
                assert result == []

    def test_get_adapter_returns_hdc(self):
        """get_adapter('hdc') returns a SourceAdapter."""
        adapter = get_adapter("hdc")
        assert isinstance(adapter, SourceAdapter)
        assert adapter.source_id == "hdc"


# ===========================================================================
# HPDT
# ===========================================================================

class TestHpdtAdapter:
    """Tests for HpdtSourceAdapter."""

    def test_imports(self):
        """HpdtSourceAdapter is importable."""
        assert HpdtSourceAdapter is not None

    def test_extends_base(self):
        """HpdtSourceAdapter extends SourceAdapter."""
        assert issubclass(HpdtSourceAdapter, SourceAdapter)

    def test_fetch_returns_list(self):
        """fetch() returns a list."""
        adapter = HpdtSourceAdapter(source_id="hpdt", config_path=Path("config/hpdt_pipeline.yaml"))
        result = adapter.fetch()
        assert isinstance(result, list)

    def test_process_sets_source(self):
        """process() sets source field to 'hpdt'."""
        adapter = HpdtSourceAdapter(source_id="hpdt", config_path=Path("config/hpdt_pipeline.yaml"))
        cases = [{"case_id": "HPDT-001", "text": "test"}]
        result = adapter.process(cases)
        assert result[0]["source"] == "hpdt"

    def test_process_sets_metadata(self):
        """process() sets metadata dict on each case."""
        adapter = HpdtSourceAdapter(source_id="hpdt", config_path=Path("config/hpdt_pipeline.yaml"))
        cases = [{"case_id": "HPDT-001"}]
        result = adapter.process(cases)
        assert "metadata" in result[0]

    def test_validate_valid(self):
        """validate() returns True for a complete case."""
        adapter = HpdtSourceAdapter(source_id="hpdt", config_path=Path("config/hpdt_pipeline.yaml"))
        case = {
            "case_id": "HPDT-001", "date": "2024-01-01",
            "title": "Test", "citation": "[2024]", "url": "https://example.com",
        }
        assert adapter.validate([case]) is True

    def test_validate_invalid_missing_fields(self):
        """validate() returns False when required fields are missing."""
        adapter = HpdtSourceAdapter(source_id="hpdt", config_path=Path("config/hpdt_pipeline.yaml"))
        case = {"case_id": "HPDT-001"}
        assert adapter.validate([case]) is False

    def test_validate_invalid_empty_case(self):
        """validate() returns False for empty dict."""
        adapter = HpdtSourceAdapter(source_id="hpdt", config_path=Path("config/hpdt_pipeline.yaml"))
        assert adapter.validate([{}]) is False

    def test_validate_multiple_cases(self):
        """validate() checks all cases in the list."""
        adapter = HpdtSourceAdapter(source_id="hpdt", config_path=Path("config/hpdt_pipeline.yaml"))
        valid = {
            "case_id": "HPDT-001", "date": "2024-01-01",
            "title": "T", "citation": "[2024]", "url": "https://ex.com",
        }
        invalid = {"case_id": "HPDT-002"}
        assert adapter.validate([valid]) is True
        assert adapter.validate([valid, invalid]) is False

    def test_fetch_mocked(self):
        """fetch() reads source_url from config (mocked)."""
        adapter = HpdtSourceAdapter(source_id="hpdt", config_path=Path("config/hpdt_pipeline.yaml"))
        with patch("corpus_cases_medilegal_nz.sources.hpdt.load_pipeline_config") as mock_load:
            mock_cfg = MagicMock()
            mock_cfg.pipeline.source_url = "https://www.hpdt.org.nz/Search-Decisions"
            mock_load.return_value = mock_cfg

            with patch.object(adapter, "_build_session") as mock_build:
                mock_session = MagicMock()
                mock_resp = MagicMock(text="<html>stub</html>")
                mock_resp.raise_for_status.return_value = None
                mock_session.get.return_value = mock_resp
                mock_build.return_value = mock_session

                result = adapter.fetch()
                mock_session.get.assert_called_once_with(
                    "https://www.hpdt.org.nz/Search-Decisions", timeout=30
                )
                assert result == []

    def test_get_adapter_returns_base(self):
        """get_adapter('hpdt') returns a SourceAdapter."""
        adapter = get_adapter("hpdt")
        assert isinstance(adapter, SourceAdapter)
        assert adapter.source_id == "hpdt"



# ===========================================================================
# MoJ Tribunals
# ===========================================================================

class TestMojTribunalsAdapter:
    """Tests for MojTribunalsSourceAdapter."""

    def test_imports(self):
        """MojTribunalsSourceAdapter is importable."""
        assert MojTribunalsSourceAdapter is not None

    def test_extends_base(self):
        """MojTribunalsSourceAdapter extends SourceAdapter."""
        assert issubclass(MojTribunalsSourceAdapter, SourceAdapter)

    def test_fetch_returns_list(self):
        """fetch() returns a list."""
        adapter = MojTribunalsSourceAdapter(
            source_id="moj_tribunals", config_path=Path("config/moj_tribunals_pipeline.yaml")
        )
        result = adapter.fetch()
        assert isinstance(result, list)

    def test_process_sets_source(self):
        """process() sets source field to 'moj_tribunals'."""
        adapter = MojTribunalsSourceAdapter(
            source_id="moj_tribunals", config_path=Path("config/moj_tribunals_pipeline.yaml")
        )
        cases = [{"case_id": "MOJ-001", "text": "test"}]
        result = adapter.process(cases)
        assert result[0]["source"] == "moj_tribunals"

    def test_process_sets_metadata(self):
        """process() sets metadata dict on each case."""
        adapter = MojTribunalsSourceAdapter(
            source_id="moj_tribunals", config_path=Path("config/moj_tribunals_pipeline.yaml")
        )
        cases = [{"case_id": "MOJ-001"}]
        result = adapter.process(cases)
        assert "metadata" in result[0]

    def test_validate_valid(self):
        """validate() returns True for a complete case."""
        adapter = MojTribunalsSourceAdapter(
            source_id="moj_tribunals", config_path=Path("config/moj_tribunals_pipeline.yaml")
        )
        case = {
            "case_id": "MOJ-001", "date": "2024-01-01",
            "title": "Test", "citation": "[2024]", "url": "https://example.com",
        }
        assert adapter.validate([case]) is True

    def test_validate_invalid(self):
        """validate() returns False when required fields are missing."""
        adapter = MojTribunalsSourceAdapter(
            source_id="moj_tribunals", config_path=Path("config/moj_tribunals_pipeline.yaml")
        )
        assert adapter.validate([{"case_id": "MOJ-001"}]) is False

    def test_validate_empty(self):
        """validate() returns False for empty dict."""
        adapter = MojTribunalsSourceAdapter(
            source_id="moj_tribunals", config_path=Path("config/moj_tribunals_pipeline.yaml")
        )
        assert adapter.validate([{}]) is False

    def test_fetch_mocked(self):
        """fetch() uses _build_session and reads config (mocked)."""
        adapter = MojTribunalsSourceAdapter(
            source_id="moj_tribunals", config_path=Path("config/moj_tribunals_pipeline.yaml")
        )
        with patch("corpus_cases_medilegal_nz.sources.moj_tribunals.load_pipeline_config") as mock_load:
            mock_cfg = MagicMock()
            mock_cfg.pipeline.source_url = "https://www.justice.govt.nz/tribunals/"
            mock_load.return_value = mock_cfg

            with patch.object(adapter, "_build_session") as mock_build:
                mock_session = MagicMock()
                mock_resp = MagicMock(text="<html>stub</html>")
                mock_resp.raise_for_status.return_value = None
                mock_session.get.return_value = mock_resp
                mock_build.return_value = mock_session

                result = adapter.fetch()
                assert result == []

    def test_get_adapter(self):
        """get_adapter('moj_tribunals') returns a SourceAdapter."""
        adapter = get_adapter("moj_tribunals")
        assert isinstance(adapter, SourceAdapter)
        assert adapter.source_id == "moj_tribunals"



# ===========================================================================
# ERA
# ===========================================================================

class TestEraAdapter:
    """Tests for EraSourceAdapter."""

    def test_imports(self):
        """EraSourceAdapter is importable."""
        assert EraSourceAdapter is not None

    def test_extends_base(self):
        """EraSourceAdapter extends SourceAdapter."""
        assert issubclass(EraSourceAdapter, SourceAdapter)

    def test_fetch_returns_list(self):
        """fetch() returns a list."""
        adapter = EraSourceAdapter(source_id="era", config_path=Path("config/era_pipeline.yaml"))
        result = adapter.fetch()
        assert isinstance(result, list)

    def test_process_sets_source(self):
        """process() sets source field to 'era'."""
        adapter = EraSourceAdapter(source_id="era", config_path=Path("config/era_pipeline.yaml"))
        cases = [{"case_id": "ERA-001", "text": "test"}]
        result = adapter.process(cases)
        assert result[0]["source"] == "era"

    def test_process_sets_metadata(self):
        """process() sets metadata dict on each case."""
        adapter = EraSourceAdapter(source_id="era", config_path=Path("config/era_pipeline.yaml"))
        cases = [{"case_id": "ERA-001"}]
        result = adapter.process(cases)
        assert "metadata" in result[0]

    def test_validate_valid(self):
        """validate() returns True for a complete case."""
        adapter = EraSourceAdapter(source_id="era", config_path=Path("config/era_pipeline.yaml"))
        case = {
            "case_id": "ERA-001", "date": "2024-01-01",
            "title": "Test", "citation": "[2024]", "url": "https://example.com",
        }
        assert adapter.validate([case]) is True

    def test_validate_invalid(self):
        """validate() returns False when required fields are missing."""
        adapter = EraSourceAdapter(source_id="era", config_path=Path("config/era_pipeline.yaml"))
        assert adapter.validate([{"case_id": "ERA-001"}]) is False

    def test_validate_empty(self):
        """validate() returns False for empty dict."""
        adapter = EraSourceAdapter(source_id="era", config_path=Path("config/era_pipeline.yaml"))
        assert adapter.validate([{}]) is False

    def test_fetch_mocked(self):
        """fetch() uses _build_session and reads config (mocked)."""
        adapter = EraSourceAdapter(source_id="era", config_path=Path("config/era_pipeline.yaml"))
        with patch("corpus_cases_medilegal_nz.sources.era.load_pipeline_config") as mock_load:
            mock_cfg = MagicMock()
            mock_cfg.pipeline.source_url = "https://www.era.govt.nz/"
            mock_load.return_value = mock_cfg

            with patch.object(adapter, "_build_session") as mock_build:
                mock_session = MagicMock()
                mock_resp = MagicMock(text="<html>stub</html>")
                mock_resp.raise_for_status.return_value = None
                mock_session.get.return_value = mock_resp
                mock_build.return_value = mock_session

                result = adapter.fetch()
                assert result == []

    def test_get_adapter(self):
        """get_adapter('era') returns a SourceAdapter."""
        adapter = get_adapter("era")
        assert isinstance(adapter, SourceAdapter)
        assert adapter.source_id == "era"



# ===========================================================================
# Teachers
# ===========================================================================

class TestTeachersAdapter:
    """Tests for TeachersSourceAdapter."""

    def test_imports(self):
        """TeachersSourceAdapter is importable."""
        assert TeachersSourceAdapter is not None

    def test_extends_base(self):
        """TeachersSourceAdapter extends SourceAdapter."""
        assert issubclass(TeachersSourceAdapter, SourceAdapter)

    def test_fetch_returns_list(self):
        """fetch() returns a list."""
        adapter = TeachersSourceAdapter(
            source_id="teachers", config_path=Path("config/teachers_pipeline.yaml")
        )
        result = adapter.fetch()
        assert isinstance(result, list)

    def test_process_sets_source(self):
        """process() sets source field to 'teachers'."""
        adapter = TeachersSourceAdapter(
            source_id="teachers", config_path=Path("config/teachers_pipeline.yaml")
        )
        cases = [{"case_id": "TDT-001", "text": "test"}]
        result = adapter.process(cases)
        assert result[0]["source"] == "teachers"

    def test_process_sets_metadata(self):
        """process() sets metadata dict on each case."""
        adapter = TeachersSourceAdapter(
            source_id="teachers", config_path=Path("config/teachers_pipeline.yaml")
        )
        cases = [{"case_id": "TDT-001"}]
        result = adapter.process(cases)
        assert "metadata" in result[0]

    def test_validate_valid(self):
        """validate() returns True for a complete case."""
        adapter = TeachersSourceAdapter(
            source_id="teachers", config_path=Path("config/teachers_pipeline.yaml")
        )
        case = {
            "case_id": "TDT-001", "date": "2024-01-01",
            "title": "Test", "citation": "[2024]", "url": "https://example.com",
        }
        assert adapter.validate([case]) is True

    def test_validate_invalid(self):
        """validate() returns False when required fields are missing."""
        adapter = TeachersSourceAdapter(
            source_id="teachers", config_path=Path("config/teachers_pipeline.yaml")
        )
        assert adapter.validate([{"case_id": "TDT-001"}]) is False

    def test_validate_empty(self):
        """validate() returns False for empty dict."""
        adapter = TeachersSourceAdapter(
            source_id="teachers", config_path=Path("config/teachers_pipeline.yaml")
        )
        assert adapter.validate([{}]) is False

    def test_fetch_mocked(self):
        """fetch() uses _build_session and reads config (mocked)."""
        adapter = TeachersSourceAdapter(
            source_id="teachers", config_path=Path("config/teachers_pipeline.yaml")
        )
        with patch("corpus_cases_medilegal_nz.sources.teachers.load_pipeline_config") as mock_load:
            mock_cfg = MagicMock()
            mock_cfg.pipeline.source_url = "https://www.teachersdisciplinarytribunal.nz/"
            mock_load.return_value = mock_cfg

            with patch.object(adapter, "_build_session") as mock_build:
                mock_session = MagicMock()
                mock_resp = MagicMock(text="<html>stub</html>")
                mock_resp.raise_for_status.return_value = None
                mock_session.get.return_value = mock_resp
                mock_build.return_value = mock_session

                result = adapter.fetch()
                assert result == []

    def test_get_adapter(self):
        """get_adapter('teachers') returns a SourceAdapter."""
        adapter = get_adapter("teachers")
        assert isinstance(adapter, SourceAdapter)
        assert adapter.source_id == "teachers"

