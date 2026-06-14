"""Source registry and base adapter for multi-source corpus pipeline."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

SOURCE_REGISTRY: dict[str, dict[str, Any]] = {
    "hdc": {"name": "Health and Disability Commissioner", "url": "https://www.hdc.org.nz/decisions/search-decisions/", "config": "config/hdc_pipeline.yaml"},
    "hpdt": {"name": "Health Practitioners Disciplinary Tribunal", "url": "https://www.hpdt.org.nz/Search-Decisions", "config": "config/hpdt_pipeline.yaml"},
    "moj_tribunals": {"name": "Ministry of Justice Tribunals", "url": "https://www.justice.govt.nz/tribunals/", "config": "config/moj_tribunals_pipeline.yaml"},
    "era": {"name": "Employment Relations Authority", "url": "https://www.era.govt.nz/", "config": "config/era_pipeline.yaml"},
    "teachers": {"name": "Teachers Disciplinary Tribunal", "url": "https://www.teachersdisciplinarytribunal.nz/", "config": "config/teachers_pipeline.yaml"},
    "royal_commissions": {"name": "Royal Commissions & Waitangi Tribunal", "url": "", "config": "config/royal_commissions_pipeline.yaml"},
    "coronial": {"name": "Coronial Decisions", "url": "", "config": "config/coronial_pipeline.yaml"},
    "privacy": {"name": "Privacy Commissioner", "url": "", "config": "config/privacy_pipeline.yaml"},
    "human_rights": {"name": "Human Rights Commission/Tribunal", "url": "", "config": "config/human_rights_pipeline.yaml"},
    "ombudsman": {"name": "Ombudsman Reports", "url": "", "config": "config/ombudsman_pipeline.yaml"},
    "moj_courts": {"name": "Ministry of Justice Court Cases", "url": "", "config": "config/moj_courts_pipeline.yaml"},
    "ipca": {"name": "Independent Police Conduct Authority", "url": "", "config": "config/ipca_pipeline.yaml"},
    "law_commission": {"name": "Law Commission Reports", "url": "", "config": "config/law_commission_pipeline.yaml"},
}


@dataclass
class SourceAdapter:
    """Base source adapter. Subclass for source-specific logic."""
    source_id: str
    config_path: Path
    raw_dir: Path = field(init=False)
    processed_dir: Path = field(init=False)

    def __post_init__(self) -> None:
        self.raw_dir = Path("data/raw") / self.source_id
        self.processed_dir = Path("data/processed")

    def fetch(self, **kwargs: Any) -> list[dict[str, Any]]:
        """Fetch cases from source. Override in subclasses."""
        return []

    def process(self, raw_cases: list[dict[str, Any]], **kwargs: Any) -> list[dict[str, Any]]:
        """Process raw cases. Override in subclasses."""
        return raw_cases

    def validate(self, cases: list[dict[str, Any]]) -> bool:
        """Validate processed cases."""
        return True


def get_source_ids() -> list[str]:
    """Return all registered source IDs."""
    return list(SOURCE_REGISTRY.keys())


def get_source_info(source_id: str) -> dict[str, Any]:
    """Return source registry info."""
    return SOURCE_REGISTRY[source_id]


def get_adapter(source_id: str) -> SourceAdapter:
    """Get a SourceAdapter for the given source ID."""
    info = get_source_info(source_id)
    return SourceAdapter(
        source_id=source_id,
        config_path=Path(info["config"]),
    )
