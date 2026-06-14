"""HDC source adapter."""
from __future__ import annotations

import logging
from typing import Any

from corpus_cases_medilegal_nz.config_models import HdcPipelineConfig, load_pipeline_config
from corpus_cases_medilegal_nz.fetcher import HdcFetcher
from corpus_cases_medilegal_nz.sources import SourceAdapter

logger = logging.getLogger(__name__)

REQUIRED_FIELDS = {"case_id", "date", "title", "commissioner", "citation", "url"}


class HdcSourceAdapter(SourceAdapter):
    """Adapter for HDC decision documents."""

    def fetch(self, **kwargs: Any) -> list[dict[str, Any]]:
        config = load_pipeline_config(self.config_path)
        hdc_config = HdcPipelineConfig()  # use defaults for fetch

        with HdcFetcher(hdc_config) as fetcher:
            # Fetch search page
            search_url = str(config.pipeline.source_url)
            response = fetcher.fetch_url(search_url)

            # Parse case links from response (stub — real parsing in nlp_policy_nz)
            cases: list[dict[str, Any]] = []
            logger.info("Fetched search page (%d bytes) from %s", len(response.text), search_url)

            # Return raw case data dicts
            return cases

    def process(self, raw_cases: list[dict[str, Any]], **kwargs: Any) -> list[dict[str, Any]]:
        processed = []
        for case in raw_cases:
            case.setdefault("source", "hdc")
            case.setdefault("metadata", {})
            processed.append(case)
        return processed

    def validate(self, cases: list[dict[str, Any]]) -> bool:
        for case in cases:
            missing = REQUIRED_FIELDS - set(case.keys())
            if missing:
                logger.warning("Case %s missing fields: %s", case.get("case_id", "?"), missing)
                return False
        return True
