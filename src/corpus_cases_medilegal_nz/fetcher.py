"""Raw document fetching wrapper for HDC decisions.

Delegates HTTP operations to ``requests`` with retry logic.
Actual scraping/parsing logic will live in ``nlp_policy_nz``.
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from .config_models import HdcPipelineConfig

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Data types
# ---------------------------------------------------------------------------


@dataclass
class FetchedCase:
    """Represents a single fetched HDC case document.

    Attributes
    ----------
    case_id : str
        Unique identifier for the case.
    source_url : str
        Original URL from which the document was fetched.
    raw_bytes : bytes
        Raw content of the document.
    content_type : str
        MIME type of the fetched document (e.g. ``application/pdf``).
    metadata : dict
        Additional metadata extracted during fetch.
    """

    case_id: str
    source_url: str
    raw_bytes: bytes
    content_type: str = "application/octet-stream"
    metadata: dict[str, Any] = field(default_factory=dict)


# ---------------------------------------------------------------------------
# Fetcher
# ---------------------------------------------------------------------------


class HdcFetcher:
    """Fetcher for HDC decision documents.

    Wraps ``requests`` with retry logic configured from the pipeline config.
    This is a lightweight wrapper; heavy scraping logic is delegated to
    ``nlp_policy_nz``.

    Parameters
    ----------
    config : HdcPipelineConfig
        Pipeline configuration with fetch settings.
    """

    def __init__(self, config: HdcPipelineConfig) -> None:
        self._config = config
        self._session = self._build_session()

    def _build_session(self) -> requests.Session:
        """Build a ``requests.Session`` with retry logic."""
        session = requests.Session()

        fetch_cfg = self._config.fetch
        retries = Retry(
            total=fetch_cfg.retry_attempts,
            backoff_factor=fetch_cfg.retry_backoff_base_seconds,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET"],
        )
        adapter = HTTPAdapter(max_retries=retries)
        session.mount("https://", adapter)
        session.mount("http://", adapter)

        session.headers.update(
            {
                "User-Agent": fetch_cfg.user_agent,
                "Accept": "text/html,application/pdf,*/*",
            }
        )
        return session

    def fetch_url(self, url: str, timeout: int | None = None) -> requests.Response:
        """Fetch a URL with rate limiting and timeout.

        Parameters
        ----------
        url : str
            The URL to fetch.
        timeout : int | None
            Request timeout in seconds. Falls back to config value.

        Returns
        -------
        requests.Response
            The HTTP response.

        Raises
        ------
        requests.RequestException
            If the request fails after all retries.
        """
        rate = self._config.fetch.rate_limit_per_second
        if rate > 0:
            time.sleep(1.0 / rate)

        fetch_cfg = self._config.fetch
        actual_timeout = timeout if timeout is not None else fetch_cfg.request_timeout_seconds

        resp = self._session.get(url, timeout=actual_timeout)
        resp.raise_for_status()
        return resp

    def fetch_case(self, url: str, case_id: str | None = None) -> FetchedCase:
        """Fetch a single case document by URL.

        Parameters
        ----------
        url : str
            The URL of the case document.
        case_id : str | None
            Optional case identifier. Auto-generated from URL if not provided.

        Returns
        -------
        FetchedCase
            The fetched case document.
        """
        resp = self.fetch_url(url)
        cid = case_id or Path(url).stem
        content_type = resp.headers.get("Content-Type", "application/octet-stream")

        return FetchedCase(
            case_id=cid,
            source_url=url,
            raw_bytes=resp.content,
            content_type=content_type,
            metadata={"status_code": resp.status_code},
        )

    def close(self) -> None:
        """Close the underlying HTTP session."""
        self._session.close()

    def __enter__(self) -> HdcFetcher:
        return self

    def __exit__(self, *args: Any) -> None:
        self.close()


# ---------------------------------------------------------------------------
# Convenience function
# ---------------------------------------------------------------------------


def fetch_case(
    url: str,
    config: HdcPipelineConfig | None = None,
    case_id: str | None = None,
) -> FetchedCase:
    """Convenience function to fetch a single case.

    Parameters
    ----------
    url : str
        The URL of the case document.
    config : HdcPipelineConfig | None
        Pipeline configuration. A default config is used if ``None``.
    case_id : str | None
        Optional case identifier.

    Returns
    -------
    FetchedCase
        The fetched case document.
    """
    cfg = config if config is not None else HdcPipelineConfig()
    with HdcFetcher(cfg) as fetcher:
        return fetcher.fetch_case(url, case_id=case_id)
