"""Source-specific parser profiles layered over the shared listing parser."""

from __future__ import annotations

from typing import Any

from corpus_cases_medilegal_nz.medilegal_parser import parse_source_listing_html
from corpus_cases_medilegal_nz.source_maturity import HIGH_RISK_GENERIC_PARSER_SOURCES

JsonObject = dict[str, Any]

SOURCE_SPECIFIC_PARSER_PROFILES: dict[str, JsonObject] = {
    "acc_appeals_reviews": {
        "profile_id": "acc_appeals_reviews_listing_v1",
        "record_kinds": ["appeal decision", "review decision", "summary order"],
        "required_evidence": ["appeal index", "detail page", "source-specific identifier"],
    },
    "social_security_appeal_authority": {
        "profile_id": "social_security_appeal_authority_listing_v1",
        "record_kinds": ["appeal decision", "medical appeal", "benefit review"],
        "required_evidence": ["appeal index", "detail page", "source-specific identifier"],
    },
    "mental_health_review_tribunal": {
        "profile_id": "mental_health_review_tribunal_listing_v1",
        "record_kinds": ["tribunal decision", "order", "summary"],
        "required_evidence": ["tribunal index", "detail page", "source-specific identifier"],
    },
    "nzlii_health_privacy_discipline": {
        "profile_id": "nzlii_health_privacy_discipline_listing_v1",
        "record_kinds": ["case", "tribunal decision", "disciplinary decision"],
        "required_evidence": ["search results", "detail page", "source-specific identifier"],
    },
    "moj_tribunals": {
        "profile_id": "moj_tribunals_listing_v1",
        "record_kinds": ["tribunal decision", "tribunal order", "public report"],
        "required_evidence": ["pagination", "detail page", "source-specific identifier"],
    },
    "royal_commissions": {
        "profile_id": "royal_commissions_waitangi_reports_v1",
        "record_kinds": ["tribunal report", "inquiry report", "commission report"],
        "required_evidence": ["report listing", "document asset", "source-specific identifier"],
    },
    "coronial": {
        "profile_id": "coronial_findings_v1",
        "record_kinds": ["finding", "recommendation", "case summary"],
        "required_evidence": ["finding page", "date", "source-specific identifier"],
    },
    "ombudsman": {
        "profile_id": "ombudsman_resources_v1",
        "record_kinds": ["case note", "opinion", "investigation report"],
        "required_evidence": ["resource listing", "document asset", "date"],
    },
    "moj_courts": {
        "profile_id": "moj_courts_jdo_v1",
        "record_kinds": ["judgment", "decision", "sentencing note"],
        "required_evidence": ["JDO listing", "detail page", "neutral citation"],
    },
    "ipca": {
        "profile_id": "ipca_accountability_archive_v1",
        "record_kinds": ["report", "accountability finding", "media release"],
        "required_evidence": ["archive listing", "report URL", "date"],
    },
    "law_commission": {
        "profile_id": "law_commission_reports_v1",
        "record_kinds": ["report", "issues paper", "ministerial briefing"],
        "required_evidence": ["project listing", "document asset", "publication date"],
    },
}


def source_specific_profile_status(source_id: str) -> str:
    """Return parser-proof status for a source."""
    if source_id in SOURCE_SPECIFIC_PARSER_PROFILES:
        return "source_specific_parser_proven"
    if source_id in HIGH_RISK_GENERIC_PARSER_SOURCES:
        return "source_specific_parser_required"
    return "selector_drift_review_required"


def parse_source_specific_listing_html(
    *,
    source_id: str,
    url: str,
    html: str,
    retrieved_at: str | None = None,
) -> list[JsonObject]:
    """Parse using a source-specific proof profile and attach parser provenance."""
    profile = SOURCE_SPECIFIC_PARSER_PROFILES.get(source_id)
    if profile is None:
        msg = f"No source-specific parser profile registered for {source_id}"
        raise KeyError(msg)
    records = parse_source_listing_html(
        source_id=source_id,
        url=url,
        html=html,
        retrieved_at=retrieved_at,
    )
    for record in records:
        metadata = record.setdefault("metadata", {})
        metadata["parser_name"] = (
            "corpus_cases_medilegal_nz.source_parser_profiles."
            f"{profile['profile_id']}"
        )
        metadata["parser_profile_id"] = profile["profile_id"]
        metadata["parser_profile_record_kinds"] = profile["record_kinds"]
        metadata["parser_profile_required_evidence"] = profile["required_evidence"]
    return records


def selector_drift_review_profiles() -> dict[str, JsonObject]:
    """Return live-smoke review profile expectations for non-high-risk sources."""
    return {
        source_id: {
            "profile_id": f"{source_id}_selector_drift_review_v1",
            "required_checks": ["reachability", "selector_drift", "robots_or_terms_posture"],
            "promotion_gate": "live_selector_drift_smoke_pass",
        }
        for source_id in ("hdc", "hpdt", "era", "teachers", "privacy", "human_rights")
    }
