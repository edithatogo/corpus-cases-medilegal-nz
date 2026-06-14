"""Tests for the ``fetcher`` module."""

from __future__ import annotations

from unittest import mock

import pytest
import requests

from corpus_cases_medilegal_nz.config_models import HdcPipelineConfig
from corpus_cases_medilegal_nz.fetcher import (
    FetchedCase,
    HdcFetcher,
    fetch_case,
)

# ---------------------------------------------------------------------------
# FetchedCase
# ---------------------------------------------------------------------------


class TestFetchedCase:
    """Tests for ``FetchedCase`` dataclass."""

    def test_minimal_construction(self) -> None:
        """A minimal FetchedCase can be built with just case_id, source_url, raw_bytes."""
        case = FetchedCase(
            case_id="HDC-001",
            source_url="https://example.com/case.pdf",
            raw_bytes=b"%PDF-1.4 mock content",
        )
        assert case.case_id == "HDC-001"
        assert case.source_url == "https://example.com/case.pdf"
        assert case.raw_bytes == b"%PDF-1.4 mock content"
        assert case.content_type == "application/octet-stream"
        assert case.metadata == {}

    def test_full_construction(self) -> None:
        """A FetchedCase can be built with all fields."""
        case = FetchedCase(
            case_id="HDC-002",
            source_url="https://example.com/case.html",
            raw_bytes=b"<html>content</html>",
            content_type="text/html",
            metadata={"status_code": 200, "source": "hdc"},
        )
        assert case.content_type == "text/html"
        assert case.metadata == {"status_code": 200, "source": "hdc"}

    def test_default_content_type(self) -> None:
        """Default content_type is application/octet-stream."""
        case = FetchedCase(case_id="id", source_url="url", raw_bytes=b"data")
        assert case.content_type == "application/octet-stream"

    def test_default_metadata_is_empty_dict(self) -> None:
        """Default metadata is an empty dict, not None."""
        case = FetchedCase(case_id="id", source_url="url", raw_bytes=b"data")
        assert case.metadata == {}

    def test_mutable_default_metadata(self) -> None:
        """Each instance gets its own metadata dict."""
        case1 = FetchedCase(case_id="id1", source_url="url1", raw_bytes=b"data1")
        case2 = FetchedCase(case_id="id2", source_url="url2", raw_bytes=b"data2")
        case1.metadata["key"] = "value"
        assert "key" not in case2.metadata


# ---------------------------------------------------------------------------
# HdcFetcher
# ---------------------------------------------------------------------------


@pytest.fixture
def default_config() -> HdcPipelineConfig:
    """Return a default HdcPipelineConfig for testing."""
    return HdcPipelineConfig()


class TestHdcFetcherInit:
    """Tests for ``HdcFetcher.__init__``."""

    def test_creates_session(self, default_config: HdcPipelineConfig) -> None:
        """``__init__`` stores the config and builds a session."""
        fetcher = HdcFetcher(default_config)
        assert fetcher._config is default_config
        assert isinstance(fetcher._session, requests.Session)


class TestHdcFetcherBuildSession:
    """Tests for ``HdcFetcher._build_session``."""

    def test_session_has_retry_adapter(
        self, default_config: HdcPipelineConfig
    ) -> None:
        """The session mounts an HTTPAdapter with Retry config."""
        fetcher = HdcFetcher(default_config)
        adapter = fetcher._session.get_adapter("https://example.com")
        assert isinstance(adapter, requests.adapters.HTTPAdapter)

    def test_session_headers_include_user_agent(
        self, default_config: HdcPipelineConfig
    ) -> None:
        """Session headers contain the configured User-Agent."""
        fetcher = HdcFetcher(default_config)
        ua = fetcher._session.headers.get("User-Agent", "")
        assert "NZ-Medicolegal-Corpus-Sync" in ua

    def test_session_headers_include_accept(
        self, default_config: HdcPipelineConfig
    ) -> None:
        """Session headers contain the Accept header."""
        fetcher = HdcFetcher(default_config)
        accept = fetcher._session.headers.get("Accept", "")
        assert accept == "text/html,application/pdf,*/*"

    def test_retry_config_matches_fetch_config(
        self, default_config: HdcPipelineConfig
    ) -> None:
        """The retry adapter uses values from the fetch config."""
        fetcher = HdcFetcher(default_config)
        adapter = fetcher._session.get_adapter("https://example.com")
        retry = adapter.max_retries
        assert retry.total == default_config.fetch.retry_attempts
        assert retry.backoff_factor == default_config.fetch.retry_backoff_base_seconds
        assert retry.status_forcelist == [429, 500, 502, 503, 504]
        assert retry.allowed_methods == ["GET"]

    def test_custom_retry_config(self) -> None:
        """A config with custom retry values propagates to the adapter."""
        cfg = HdcPipelineConfig()
        cfg.fetch.retry_attempts = 7
        cfg.fetch.retry_backoff_base_seconds = 3.0
        cfg.fetch.rate_limit_per_second = 5.0
        cfg.fetch.request_timeout_seconds = 15
        cfg.fetch.user_agent = "Custom/1.0"

        fetcher = HdcFetcher(cfg)
        adapter = fetcher._session.get_adapter("https://example.com")
        assert adapter.max_retries.total == 7
        assert adapter.max_retries.backoff_factor == 3.0

class TestHdcFetcherFetchUrl:
    """Tests for ``HdcFetcher.fetch_url``."""

    def test_successful_get(self, default_config: HdcPipelineConfig) -> None:
        """A successful GET returns the response."""
        fetcher = HdcFetcher(default_config)
        mock_resp = mock.MagicMock(spec=requests.Response)
        mock_resp.status_code = 200
        mock_resp.content = b"mock content"
        mock_resp.headers = {"Content-Type": "text/html"}
        mock_resp.raise_for_status.return_value = None

        fetcher._session = mock.MagicMock(spec=requests.Session)
        fetcher._session.get.return_value = mock_resp

        resp = fetcher.fetch_url("https://example.com/test")
        fetcher._session.get.assert_called_once_with(
            "https://example.com/test", timeout=30
        )
        assert resp.status_code == 200

    def test_custom_timeout(self, default_config: HdcPipelineConfig) -> None:
        """A custom timeout overrides the config default."""
        fetcher = HdcFetcher(default_config)
        fetcher._session = mock.MagicMock(spec=requests.Session)
        mock_resp = mock.MagicMock(spec=requests.Response)
        mock_resp.raise_for_status.return_value = None
        fetcher._session.get.return_value = mock_resp

        fetcher.fetch_url("https://example.com/test", timeout=10)
        fetcher._session.get.assert_called_once_with(
            "https://example.com/test", timeout=10
        )


class TestHdcFetcherFetchCase:
    """Tests for ``HdcFetcher.fetch_case``."""

    def test_fetch_case_returns_fetched_case(
        self, default_config: HdcPipelineConfig
    ) -> None:
        """``fetch_case`` returns a FetchedCase with correct fields."""
        fetcher = HdcFetcher(default_config)
        mock_resp = mock.MagicMock(spec=requests.Response)
        mock_resp.status_code = 200
        mock_resp.content = b"%PDF-1.4 mock pdf content"
        mock_resp.headers = {"Content-Type": "application/pdf"}
        mock_resp.raise_for_status.return_value = None

        fetcher._session = mock.MagicMock(spec=requests.Session)
        fetcher._session.get.return_value = mock_resp

        result = fetcher.fetch_case("https://example.com/decision-123.pdf")
        assert isinstance(result, FetchedCase)
        assert result.case_id == "decision-123"
        assert result.source_url == "https://example.com/decision-123.pdf"
        assert result.raw_bytes == b"%PDF-1.4 mock pdf content"
        assert result.content_type == "application/pdf"
        assert result.metadata == {"status_code": 200}

    def test_fetch_case_with_custom_id(
        self, default_config: HdcPipelineConfig
    ) -> None:
        """A custom ``case_id`` is used when provided."""
        fetcher = HdcFetcher(default_config)
        mock_resp = mock.MagicMock(spec=requests.Response)
        mock_resp.status_code = 200
        mock_resp.content = b"data"
        mock_resp.headers = {}
        mock_resp.raise_for_status.return_value = None

        fetcher._session = mock.MagicMock(spec=requests.Session)
        fetcher._session.get.return_value = mock_resp

        result = fetcher.fetch_case(
            "https://example.com/decision-456.pdf",
            case_id="HDC-2024-456",
        )
        assert result.case_id == "HDC-2024-456"

    def test_context_manager(self, default_config: HdcPipelineConfig) -> None:
        """``HdcFetcher`` can be used as a context manager."""
        with HdcFetcher(default_config) as fetcher:
            assert isinstance(fetcher, HdcFetcher)

    def test_close_closes_session(self, default_config: HdcPipelineConfig) -> None:
        """``close`` closes the underlying session."""
        fetcher = HdcFetcher(default_config)
        fetcher._session = mock.MagicMock(spec=requests.Session)
        fetcher.close()
        fetcher._session.close.assert_called_once()


# ---------------------------------------------------------------------------
# Convenience function: fetch_case
# ---------------------------------------------------------------------------


class TestConvenienceFetchCase:
    """Tests for the ``fetch_case`` convenience function."""

    def test_fetch_case_with_default_config(self) -> None:
        """``fetch_case`` works with default config when none is provided."""
        with mock.patch(
            "corpus_cases_medilegal_nz.fetcher.HdcFetcher"
        ) as MockFetcher:
            mock_instance = MockFetcher.return_value.__enter__.return_value
            mock_instance.fetch_case.return_value = FetchedCase(
                case_id="HDC-999",
                source_url="https://example.com/doc",
                raw_bytes=b"data",
                content_type="text/html",
                metadata={"status_code": 200},
            )

            result = fetch_case("https://example.com/doc")
            assert isinstance(result, FetchedCase)
            assert result.case_id == "HDC-999"
            MockFetcher.assert_called_once()
            mock_instance.fetch_case.assert_called_once_with(
                "https://example.com/doc", case_id=None
            )

    def test_fetch_case_with_explicit_config(self) -> None:
        """``fetch_case`` uses the provided config."""
        config = HdcPipelineConfig()
        with mock.patch(
            "corpus_cases_medilegal_nz.fetcher.HdcFetcher"
        ) as MockFetcher:
            mock_instance = MockFetcher.return_value.__enter__.return_value
            mock_instance.fetch_case.return_value = FetchedCase(
                case_id="HDC-888",
                source_url="https://example.com/doc",
                raw_bytes=b"data",
            )

            result = fetch_case("https://example.com/doc", config=config)
            MockFetcher.assert_called_once_with(config)
            assert result.case_id == "HDC-888"

    def test_fetch_case_with_case_id(self) -> None:
        """``fetch_case`` passes the case_id to the fetcher."""
        with mock.patch(
            "corpus_cases_medilegal_nz.fetcher.HdcFetcher"
        ) as MockFetcher:
            mock_instance = MockFetcher.return_value.__enter__.return_value
            mock_instance.fetch_case.return_value = FetchedCase(
                case_id="EXPLICIT-ID",
                source_url="https://example.com/doc",
                raw_bytes=b"data",
            )

            result = fetch_case(
                "https://example.com/doc",
                case_id="EXPLICIT-ID",
            )
            mock_instance.fetch_case.assert_called_once_with(
                "https://example.com/doc", case_id="EXPLICIT-ID"
            )
            assert result.case_id == "EXPLICIT-ID"

