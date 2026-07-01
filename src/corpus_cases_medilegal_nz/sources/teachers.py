"""Teachers Disciplinary Tribunal source adapter."""

from __future__ import annotations

import logging
from typing import Any

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from corpus_cases_medilegal_nz.config_models import load_pipeline_config
from corpus_cases_medilegal_nz.medilegal_parser import parse_source_listing_html
from corpus_cases_medilegal_nz.sources import SourceAdapter

logger = logging.getLogger(__name__)

REQUIRED_FIELDS = {"case_id", "date", "title", "citation", "url"}


class TeachersSourceAdapter(SourceAdapter):
    """Adapter for Teachers Disciplinary Tribunal decision documents."""

    def _build_session(self) -> requests.Session:
        session = requests.Session()
        retries = Retry(total=3, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504])
        session.mount("https://", HTTPAdapter(max_retries=retries))
        session.headers.update(
            {"User-Agent": "Mozilla/5.0 (compatible; NZ-Medicolegal-Corpus-Sync/1.0)"}
        )
        return session

    def fetch(self) -> list[dict[str, Any]]:
        """Fetch and parse Teachers Tribunal listing records."""
        config = load_pipeline_config(self.config_path)
        session = self._build_session()
        try:
            url = str(config.pipeline.source_url)
            resp = session.get(url, timeout=30)
            resp.raise_for_status()
            logger.info(
                "Fetched Teachers Disciplinary Tribunal search page (%d bytes)", len(resp.text)
            )
            return parse_source_listing_html(source_id="teachers", url=url, html=resp.text)
        finally:
            session.close()

    def process(self, raw_cases: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Ensure Teachers Tribunal records carry source and metadata containers."""
        for case in raw_cases:
            case.setdefault("source", "teachers")
            case.setdefault("metadata", {})
        return raw_cases

    def validate(self, cases: list[dict[str, Any]]) -> bool:
        """Return whether all Teachers Tribunal records contain the required fields."""
        for case in cases:
            missing = REQUIRED_FIELDS - set(case.keys())
            if missing:
                logger.warning("Case %s missing fields: %s", case.get("case_id", "?"), missing)
                return False
        return True
