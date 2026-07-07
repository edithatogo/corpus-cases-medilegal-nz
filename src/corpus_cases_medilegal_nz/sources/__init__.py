"""Source registry and base adapter for multi-source corpus pipeline."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

SOURCE_REGISTRY: dict[str, dict[str, Any]] = {
    "hdc": {"name": "Health and Disability Commissioner", "url": "https://www.hdc.org.nz/decisions/search-decisions/", "config": "config/hdc_pipeline.yaml"},
    "hpdt": {"name": "Health Practitioners Disciplinary Tribunal", "url": "https://www.hpdt.org.nz/Search-Decisions", "config": "config/hpdt_pipeline.yaml"},
    "acc_appeals_reviews": {"name": "ACC Appeals and Reviews", "url": "https://www.justice.govt.nz/tribunals/accident-compensation/older-accdcr/", "config": "config/candidates/acc_appeals_reviews_pipeline.yaml"},
    "social_security_appeal_authority": {"name": "Social Security Appeal Authority", "url": "https://www.justice.govt.nz/tribunals/social-security-appeal-authority/", "config": "config/candidates/social_security_appeal_authority_pipeline.yaml"},
    "mental_health_review_tribunal": {"name": "Mental Health Review Tribunal", "url": "https://www.health.govt.nz/about-us/new-zealands-health-system/health-system-roles-and-organisations/health-committees-and-boards/mental-health-review-tribunal", "config": "config/candidates/mental_health_review_tribunal_pipeline.yaml"},
    "moj_tribunals": {"name": "Ministry of Justice Tribunals", "url": "https://www.justice.govt.nz/tribunals/", "config": "config/moj_tribunals_pipeline.yaml"},
    "era": {"name": "Employment Relations Authority", "url": "https://www.era.govt.nz/", "config": "config/era_pipeline.yaml"},
    "teachers": {"name": "Teachers Disciplinary Tribunal", "url": "https://www.teachersdisciplinarytribunal.nz/", "config": "config/teachers_pipeline.yaml"},
    "royal_commissions": {"name": "Royal Commissions & Waitangi Tribunal", "url": "https://www.waitangitribunal.govt.nz/en/publications/tribunal-reports", "config": "config/royal_commissions_pipeline.yaml"},
    "coronial": {"name": "Coronial Decisions", "url": "https://coronialservices.justice.govt.nz/", "config": "config/coronial_pipeline.yaml"},
    "privacy": {"name": "Privacy Commissioner", "url": "https://www.privacy.org.nz/resources-and-learning/case-notes-and-court-decisions/", "config": "config/privacy_pipeline.yaml"},
    "human_rights": {"name": "Human Rights Commission/Tribunal", "url": "https://www.justice.govt.nz/tribunals/human-rights/hrrt-decisions/", "config": "config/human_rights_pipeline.yaml"},
    "ombudsman": {"name": "Ombudsman Reports", "url": "https://www.ombudsman.parliament.nz/resources", "config": "config/ombudsman_pipeline.yaml"},
    "moj_courts": {"name": "Ministry of Justice Court Cases", "url": "https://www.justice.govt.nz/courts/decisions/jdo/", "config": "config/moj_courts_pipeline.yaml"},
    "ipca": {"name": "Independent Police Conduct Authority", "url": "https://www.ipca.govt.nz/Site/publications-and-media/Accountability/Archive.aspx", "config": "config/ipca_pipeline.yaml"},
    "law_commission": {"name": "Law Commission Reports", "url": "https://www.lawcom.govt.nz/our-work", "config": "config/law_commission_pipeline.yaml"},
    "nzlii_health_privacy_discipline": {"name": "NZLII health, privacy, and discipline subsets", "url": "https://www.nzlii.org/", "config": "config/candidates/nzlii_health_privacy_discipline_pipeline.yaml"},
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
    adapter_cls: type[SourceAdapter] = SourceAdapter
    if source_id == "hdc":
        from corpus_cases_medilegal_nz.sources.hdc import HdcSourceAdapter

        adapter_cls = HdcSourceAdapter
    elif source_id == "hpdt":
        from corpus_cases_medilegal_nz.sources.hpdt import HpdtSourceAdapter

        adapter_cls = HpdtSourceAdapter
    elif source_id == "acc_appeals_reviews":
        from corpus_cases_medilegal_nz.sources.acc_appeals_reviews import (
            AccAppealsReviewsSourceAdapter,
        )

        adapter_cls = AccAppealsReviewsSourceAdapter
    elif source_id == "social_security_appeal_authority":
        from corpus_cases_medilegal_nz.sources.social_security_appeal_authority import (
            SocialSecurityAppealAuthoritySourceAdapter,
        )

        adapter_cls = SocialSecurityAppealAuthoritySourceAdapter
    elif source_id == "mental_health_review_tribunal":
        from corpus_cases_medilegal_nz.sources.mental_health_review_tribunal import (
            MentalHealthReviewTribunalSourceAdapter,
        )

        adapter_cls = MentalHealthReviewTribunalSourceAdapter
    elif source_id == "moj_tribunals":
        from corpus_cases_medilegal_nz.sources.moj_tribunals import MojTribunalsSourceAdapter

        adapter_cls = MojTribunalsSourceAdapter
    elif source_id == "era":
        from corpus_cases_medilegal_nz.sources.era import EraSourceAdapter

        adapter_cls = EraSourceAdapter
    elif source_id == "teachers":
        from corpus_cases_medilegal_nz.sources.teachers import TeachersSourceAdapter

        adapter_cls = TeachersSourceAdapter
    elif source_id == "privacy":
        from corpus_cases_medilegal_nz.sources.privacy import PrivacySourceAdapter

        adapter_cls = PrivacySourceAdapter
    elif source_id == "human_rights":
        from corpus_cases_medilegal_nz.sources.human_rights import HumanRightsSourceAdapter

        adapter_cls = HumanRightsSourceAdapter
    elif source_id == "ombudsman":
        from corpus_cases_medilegal_nz.sources.ombudsman import OmbudsmanSourceAdapter

        adapter_cls = OmbudsmanSourceAdapter
    elif source_id == "ipca":
        from corpus_cases_medilegal_nz.sources.ipca import IpcaSourceAdapter

        adapter_cls = IpcaSourceAdapter
    elif source_id == "law_commission":
        from corpus_cases_medilegal_nz.sources.law_commission import LawCommissionSourceAdapter

        adapter_cls = LawCommissionSourceAdapter
    elif source_id == "royal_commissions":
        from corpus_cases_medilegal_nz.sources.royal_commissions import RoyalCommissionsSourceAdapter

        adapter_cls = RoyalCommissionsSourceAdapter
    elif source_id == "coronial":
        from corpus_cases_medilegal_nz.sources.coronial import CoronialSourceAdapter

        adapter_cls = CoronialSourceAdapter
    elif source_id == "moj_courts":
        from corpus_cases_medilegal_nz.sources.moj_courts import MojCourtsSourceAdapter

        adapter_cls = MojCourtsSourceAdapter
    elif source_id == "nzlii_health_privacy_discipline":
        from corpus_cases_medilegal_nz.sources.nzlii_health_privacy_discipline import (
            NzliiHealthPrivacyDisciplineSourceAdapter,
        )

        adapter_cls = NzliiHealthPrivacyDisciplineSourceAdapter

    return adapter_cls(
        source_id=source_id,
        config_path=Path(info["config"]),
    )
