"""Ministry of Justice Court Cases source adapter."""

from __future__ import annotations

import logging
from typing import Any

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from corpus_cases_medilegal_nz.config_models import load_pipeline_config
from corpus_cases_medilegal_nz.source_parser_profiles import parse_source_specific_listing_html
from corpus_cases_medilegal_nz.sources import SourceAdapter

logger = logging.getLogger(__name__)

REQUIRED_FIELDS = {"case_id", "date", "title", "citation", "url"}


class MojCourtsSourceAdapter(SourceAdapter):
    """Adapter for Ministry of Justice Court Cases and judicial decisions."""

    def _build_session(self) -> requests.Session:
        session = requests.Session()
        retries = Retry(total=3, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504])
        session.mount("https://", HTTPAdapter(max_retries=retries))
        session.headers.update(
            {"User-Agent": "Mozilla/5.0 (compatible; NZ-Medicolegal-Corpus-Sync/1.0)"}
        )
        return session

    def fetch(self) -> list[dict[str, Any]]:
        """Fetch and parse MoJ court listing records."""
        config = load_pipeline_config(self.config_path)
        session = self._build_session()
        try:
            url = str(config.pipeline.source_url)
            response = session.get(url, timeout=30)
            response.raise_for_status()
            logger.info("Fetched MoJ court listing page (%d bytes)", len(response.text))
            return parse_source_specific_listing_html(
                source_id="moj_courts", url=url, html=response.text
            )
        finally:
            session.close()

    def process(self, raw_cases: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Ensure MoJ court records carry source and metadata containers."""
        for case in raw_cases:
            case.setdefault("source", "moj_courts")
            case.setdefault("metadata", {})
        return raw_cases

    def validate(self, cases: list[dict[str, Any]]) -> bool:
        """Return whether all MoJ court records contain the required fields."""
        for case in cases:
            missing = REQUIRED_FIELDS - set(case.keys())
            if missing:
                logger.warning("Case %s missing fields: %s", case.get("case_id", "?"), missing)
                return False
        return True
