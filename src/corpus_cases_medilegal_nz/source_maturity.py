"""Source maturity, historical completeness, and claim-gating ledgers."""

from __future__ import annotations

import hashlib
import json
from collections import Counter, defaultdict
from collections.abc import Iterable, Mapping
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from corpus_cases_medilegal_nz.archive import (
    build_dataset_diff,
    build_source_collection_audit,
    utc_now_iso,
)
from corpus_cases_medilegal_nz.sources import SOURCE_REGISTRY

JsonObject = dict[str, Any]

SOURCE_MATURITY_SCHEMA_VERSION = "1.0.0"
DEFAULT_SOURCE_TARGETS_PATH = Path("config/source_historical_targets.json")
SOURCE_MATURITY_LADDER = [
    "validated_records",
    "live_collection_ready",
    "historical_backfill_in_progress",
    "historical_backfill_complete",
    "publication_evidence_current",
    "blocked",
]

HIGH_RISK_GENERIC_PARSER_SOURCES = {
    "moj_tribunals",
    "moj_courts",
    "ombudsman",
    "ipca",
    "law_commission",
    "royal_commissions",
    "coronial",
}

PUBLIC_CLAIM_OVERSTATEMENT_PATTERNS = (
    "all cases archived",
    "all cases have been archived",
    "complete historical archive",
    "historically complete",
    "full historical collection",
)


def _record_id(record: Mapping[str, Any]) -> str:
    return str(record.get("case_id") or record.get("id") or record.get("url") or "")


def _metadata(record: Mapping[str, Any]) -> Mapping[str, Any]:
    metadata = record.get("metadata", {})
    return metadata if isinstance(metadata, Mapping) else {}


def _latest(values: Iterable[str]) -> str:
    cleaned = sorted(value for value in values if value)
    return cleaned[-1] if cleaned else ""


def _target_for_source(
    source_id: str,
    target_metadata: Mapping[str, Any] | None,
) -> JsonObject:
    default = {
        "source_id": source_id,
        "expected_count": None,
        "expected_count_confidence": "unknown",
        "source_update_cadence": "unknown",
        "date_range_start": "",
        "date_range_end": "",
        "known_limitations": [
            "Historical target count has not yet been established from the live public source."
        ],
    }
    if not target_metadata:
        return default
    source_targets = target_metadata.get("sources", target_metadata)
    if not isinstance(source_targets, Mapping):
        return default
    override = source_targets.get(source_id, {})
    if isinstance(override, Mapping):
        default.update(dict(override))
    return default


def _load_target_metadata(root: Path) -> JsonObject:
    """Load default source target metadata when present."""
    path = root / DEFAULT_SOURCE_TARGETS_PATH
    if not path.is_file():
        return {}
    loaded = json.loads(path.read_text(encoding="utf-8"))
    return loaded if isinstance(loaded, dict) else {}


def _stage_for_source(
    *,
    parser_stage: str,
    record_count: int,
    target: Mapping[str, Any],
    publication_manifest_hash: str,
) -> tuple[str, str]:
    stage = "validated_records"
    reason = "parser validation exists without historical target evidence."
    if parser_stage == "blocked":
        stage = "blocked"
        reason = "source is blocked before historical collection can start."
    else:
        expected = target.get("expected_count")
        confidence = str(target.get("expected_count_confidence", "unknown"))
        target_is_known = (
            isinstance(expected, int) and expected > 0 and confidence not in {"unknown", "blocked"}
        )
        target_is_verified = confidence in {"verified", "source_index_count", "official_count"}
        if target_is_known and target_is_verified and record_count >= expected:
            stage = (
                "publication_evidence_current"
                if publication_manifest_hash
                else "historical_backfill_complete"
            )
            reason = (
                "historical target is met and current publication evidence is linked."
                if publication_manifest_hash
                else "historical target count is met."
            )
        elif target_is_known and record_count > 0:
            stage = "historical_backfill_in_progress"
            reason = "some records exist, but target is unmet."
        elif record_count > 0:
            stage = "historical_backfill_in_progress"
            reason = "parser-validated proof records exist, but historical target is unknown."
        elif parser_stage in {"fetch_scaffold_parser_stub", "configured_no_adapter", "planned"}:
            stage = "live_collection_ready"
            reason = "source is configured but has no validated records."
    return stage, reason


def build_source_maturity_ledger(
    *,
    root: Path = Path(),
    records: Iterable[Mapping[str, Any]] = (),
    previous_records: Iterable[Mapping[str, Any]] | None = None,
    target_metadata: Mapping[str, Any] | None = None,
    publication_manifest_hash: str = "",
) -> JsonObject:
    """Build source maturity evidence beyond parser validation."""
    root = Path(root)
    if target_metadata is None:
        target_metadata = _load_target_metadata(root)
    current_records = [dict(record) for record in records]
    previous = [dict(record) for record in previous_records or []]
    audit = build_source_collection_audit(root=root, records=current_records)
    audit_by_source = {
        str(source.get("source_id", "")): source
        for source in audit.get("sources", [])
        if isinstance(source, Mapping)
    }
    current_by_source: dict[str, list[JsonObject]] = defaultdict(list)
    previous_by_source: dict[str, list[JsonObject]] = defaultdict(list)
    for record in current_records:
        current_by_source[str(record.get("source", ""))].append(record)
    for record in previous:
        previous_by_source[str(record.get("source", ""))].append(record)

    stage_counts: Counter[str] = Counter()
    sources: list[JsonObject] = []
    for source_id, info in SOURCE_REGISTRY.items():
        source_records = current_by_source[source_id]
        previous_source_records = previous_by_source[source_id]
        target = _target_for_source(source_id, target_metadata)
        parser_stage = str(audit_by_source.get(source_id, {}).get("completion_stage", "blocked"))
        record_count = len(source_records)
        maturity_stage, stage_reason = _stage_for_source(
            parser_stage=parser_stage,
            record_count=record_count,
            target=target,
            publication_manifest_hash=publication_manifest_hash,
        )
        stage_counts[maturity_stage] += 1
        dataset_diff = build_dataset_diff(source_records, previous_source_records)
        expected_count = target.get("expected_count")
        remaining_to_target = (
            max(int(expected_count) - record_count, 0) if isinstance(expected_count, int) else None
        )
        metadata_items = [_metadata(record) for record in source_records]
        source_urls = sorted(
            {
                str(record.get("url") or metadata.get("url") or "")
                for record, metadata in zip(source_records, metadata_items, strict=False)
                if str(record.get("url") or metadata.get("url") or "").strip()
            }
        )
        raw_hashes = sorted(
            {
                str(metadata.get("raw_sha256", ""))
                for metadata in metadata_items
                if str(metadata.get("raw_sha256", "")).strip()
            }
        )
        sources.append(
            {
                "source_id": source_id,
                "name": info["name"],
                "url": info.get("url", ""),
                "parser_stage": parser_stage,
                "historical_maturity_stage": maturity_stage,
                "stage_reason": stage_reason,
                "record_count": record_count,
                "previous_record_count": len(previous_source_records),
                "target": target,
                "target_progress": {
                    "expected_count": expected_count,
                    "record_count": record_count,
                    "remaining_to_target": remaining_to_target,
                    "progress_ratio": (
                        round(record_count / int(expected_count), 4)
                        if isinstance(expected_count, int) and expected_count > 0
                        else None
                    ),
                },
                "counts": {
                    "fetched": len(raw_hashes) or record_count,
                    "parsed": record_count,
                    "normalized": record_count,
                    "exported": record_count,
                    "excluded": 0,
                    "tombstoned": int(dataset_diff["counts"]["tombstoned"]),
                },
                "latest_source_date": _latest(
                    str(record.get("date", "")) for record in source_records
                ),
                "last_successful_crawl_at": _latest(
                    str(metadata.get("retrieved_at", "")) for metadata in metadata_items
                ),
                "publication_manifest_sha256": publication_manifest_hash,
                "source_urls": source_urls,
                "raw_asset_hashes": raw_hashes,
                "known_limitations": target.get("known_limitations", []),
                "next_action": _next_maturity_action(maturity_stage),
            }
        )
    complete_sources = [
        source
        for source in sources
        if source["historical_maturity_stage"]
        in {"historical_backfill_complete", "publication_evidence_current"}
    ]
    sources_with_known_targets = [
        source
        for source in sources
        if isinstance(source.get("target", {}).get("expected_count"), int)
    ]
    total_expected = sum(
        int(source["target"]["expected_count"]) for source in sources_with_known_targets
    )
    total_records_against_known_targets = sum(
        int(source["record_count"]) for source in sources_with_known_targets
    )
    return {
        "schema_version": SOURCE_MATURITY_SCHEMA_VERSION,
        "generated_at": utc_now_iso(),
        "maturity_ladder": SOURCE_MATURITY_LADDER,
        "summary": {
            "source_count": len(sources),
            "historically_complete_source_count": len(complete_sources),
            "all_sources_historically_complete": len(complete_sources) == len(sources),
            "sources_with_known_targets": len(sources_with_known_targets),
            "total_expected_records_for_known_targets": total_expected,
            "total_records_against_known_targets": total_records_against_known_targets,
            "total_remaining_to_known_targets": max(
                total_expected - total_records_against_known_targets,
                0,
            ),
            "stage_counts": dict(sorted(stage_counts.items())),
        },
        "sources": sources,
    }


def _next_maturity_action(stage: str) -> str:
    actions = {
        "validated_records": "define live backfill target and completeness evidence.",
        "live_collection_ready": "run source collection and produce validated records.",
        "historical_backfill_in_progress": "continue live backfill and reconcile against target.",
        "historical_backfill_complete": "rerun publication and verify remote manifests.",
        "publication_evidence_current": "monitor freshness, drift, and rights evidence.",
        "blocked": "resolve configuration, rights, or source-access blocker.",
    }
    return actions.get(stage, "triage source maturity.")


def build_source_completeness_ledger(
    *,
    root: Path = Path(),
    records: Iterable[Mapping[str, Any]] = (),
    previous_records: Iterable[Mapping[str, Any]] | None = None,
    target_metadata: Mapping[str, Any] | None = None,
    publication_manifest_hash: str = "",
) -> JsonObject:
    """Build a release-ready completeness reconciliation ledger."""
    maturity = build_source_maturity_ledger(
        root=root,
        records=records,
        previous_records=previous_records,
        target_metadata=target_metadata,
        publication_manifest_hash=publication_manifest_hash,
    )
    blockers = [
        f"{source['source_id']} is {source['historical_maturity_stage']}"
        for source in maturity["sources"]
        if source["historical_maturity_stage"]
        not in {"historical_backfill_complete", "publication_evidence_current"}
    ]
    return {
        "schema_version": SOURCE_MATURITY_SCHEMA_VERSION,
        "generated_at": utc_now_iso(),
        "status": "pass" if not blockers else "warn",
        "blockers": blockers,
        "summary": maturity["summary"],
        "sources": maturity["sources"],
    }


def build_source_discovery_queue() -> JsonObject:
    """Return the review-gated candidate source queue."""
    candidates = [
        {
            "candidate_id": "acc_appeals_reviews",
            "name": "ACC appeal and review material",
            "url": "https://www.acc.co.nz/",
            "document_classes": ["review", "appeal", "decision"],
            "medicolegal_relevance": "high",
            "parser_complexity": "high",
            "expected_value": "high",
            "review_status": "needs_source_review",
            "decision": "deferred",
            "decision_rationale": (
                "ACC appeal/review value is high, but public availability, rights posture, "
                "and parser scope are not yet specific enough for canonical inclusion."
            ),
            "promotion_status": "blocked_until_public_source_rights_and_parser_scope_review",
            "promotion_gate": "rights, public availability, and parser scope must be approved.",
        },
        {
            "candidate_id": "professional_councils_other",
            "name": "Professional council disciplinary material outside HPDT",
            "url": "",
            "document_classes": ["disciplinary decision", "finding"],
            "medicolegal_relevance": "high",
            "parser_complexity": "medium",
            "expected_value": "high",
            "review_status": "needs_source_discovery",
            "decision": "deferred",
            "decision_rationale": (
                "Potentially valuable disciplinary material remains source-discovery work "
                "until public council-specific sources are enumerated and deduplicated."
            ),
            "promotion_status": "blocked_until_public_sources_identified",
            "promotion_gate": "identify public sources and avoid duplication with HPDT.",
        },
        {
            "candidate_id": "mental_health_review_tribunal",
            "name": "Mental Health Review Tribunal material if public",
            "url": "https://www.justice.govt.nz/tribunals/mental-health-review-tribunal/",
            "document_classes": ["tribunal material"],
            "medicolegal_relevance": "high",
            "parser_complexity": "unknown",
            "expected_value": "medium",
            "review_status": "needs_public_availability_review",
            "decision": "deferred",
            "decision_rationale": (
                "Mental Health Review Tribunal material may be sensitive and is included "
                "only if public, redistributable source material is identified."
            ),
            "promotion_status": "blocked_until_public_availability_confirmed",
            "promotion_gate": "only public, redistributable material may be registered.",
        },
        {
            "candidate_id": "nzlii_health_privacy_discipline",
            "name": "NZLII health, privacy, and discipline subsets",
            "url": "https://www.nzlii.org/",
            "document_classes": ["case", "tribunal decision"],
            "medicolegal_relevance": "high",
            "parser_complexity": "medium",
            "expected_value": "high",
            "review_status": "needs_rights_review",
            "decision": "approved",
            "decision_rationale": (
                "Approved for implementation planning as a secondary discovery source, "
                "subject to NZLII terms, attribution, and duplicate-handling evidence."
            ),
            "promotion_status": "requires_source_config_fixture_rights_and_parser_contract",
            "promotion_gate": "confirm NZLII terms, attribution, and duplicate strategy.",
        },
        {
            "candidate_id": "health_appellate_court_filters",
            "name": "Health-related Court of Appeal and Supreme Court filters",
            "url": "https://www.courtsofnz.govt.nz/",
            "document_classes": ["judgment"],
            "medicolegal_relevance": "medium",
            "parser_complexity": "high",
            "expected_value": "medium",
            "review_status": "needs_scope_definition",
            "decision": "deferred",
            "decision_rationale": (
                "Health appellate filtering needs a defensible medicolegal scope rule "
                "before it can be promoted into canonical source coverage."
            ),
            "promotion_status": "blocked_until_scope_definition",
            "promotion_gate": "define defensible medicolegal filter and source provenance.",
        },
    ]
    decision_counts = Counter(str(candidate["decision"]) for candidate in candidates)
    return {
        "schema_version": SOURCE_MATURITY_SCHEMA_VERSION,
        "generated_at": utc_now_iso(),
        "status": "triaged",
        "promotion_policy": (
            "Approved candidates are not active registry sources until source config, "
            "fixture contract, rights review, live verification, and parser-risk evidence exist."
        ),
        "summary": {
            "candidate_count": len(candidates),
            "decision_counts": dict(sorted(decision_counts.items())),
            "approved_candidate_count": decision_counts.get("approved", 0),
            "unpromoted_candidate_count": sum(
                1
                for candidate in candidates
                if candidate["promotion_status"]
                != "ready_for_canonical_release"
            ),
        },
        "candidates": candidates,
    }


def build_source_rights_review_ledger() -> JsonObject:
    """Build conservative source-level rights review evidence."""
    terms_urls = {
        "hdc": "https://www.hdc.org.nz/about-us/about-this-site/",
        "hpdt": "https://www.hpdt.org.nz/",
        "moj_tribunals": "https://www.justice.govt.nz/about/about-this-site/",
        "era": "https://www.era.govt.nz/about-this-site/",
        "teachers": "https://www.teachersdisciplinarytribunal.nz/",
        "royal_commissions": "https://www.waitangitribunal.govt.nz/en/about/website-information",
        "coronial": "https://coronialservices.justice.govt.nz/",
        "privacy": "https://www.privacy.org.nz/about-us/about-this-website/",
        "human_rights": "https://www.justice.govt.nz/about/about-this-site/",
        "ombudsman": "https://www.ombudsman.parliament.nz/about/website-privacy-and-copyright",
        "moj_courts": "https://www.justice.govt.nz/about/about-this-site/",
        "ipca": "https://www.ipca.govt.nz/Site/other/copyright.aspx",
        "law_commission": "https://www.lawcom.govt.nz/copyright/",
    }
    sources = []
    for source_id, info in SOURCE_REGISTRY.items():
        sources.append(
            {
                "source_id": source_id,
                "name": info["name"],
                "url": info.get("url", ""),
                "status": "needs-review",
                "source_terms_url": terms_urls.get(source_id, info.get("url", "")),
                "citation_guidance": (
                    "Cite the official source URL, source name, decision/report title, "
                    "publication date, and repository release DOI when available."
                ),
                "attribution_required": True,
                "redistribution_status": "public-source-review-required",
                "privacy_caveats": [
                    "Public source may include sensitive health, discipline, employment, or complaint facts."
                ],
                "known_exclusions": [],
                "takedown_contact": "Repository maintainer via GitHub issue or configured archive contact.",
                "deidentification_caveat": "Do not infer anonymisation beyond the source publication.",
                "next_action": (
                    "Review source terms and privacy posture before asserting redistribution "
                    "or complete-corpus claims."
                ),
            }
        )
    return {
        "schema_version": SOURCE_MATURITY_SCHEMA_VERSION,
        "generated_at": utc_now_iso(),
        "status": "review_required",
        "sources": sources,
    }


def validate_source_rights_review_ledger(ledger: Mapping[str, Any]) -> JsonObject:
    """Validate source rights ledger completeness and unresolved review blockers."""
    sources = [source for source in ledger.get("sources", []) if isinstance(source, Mapping)]
    blockers: list[str] = []
    warnings: list[str] = []
    for source in sources:
        source_id = str(source.get("source_id", "unknown"))
        if str(source.get("status", "")) != "reviewed":
            blockers.append(f"{source_id}:rights_review_unresolved")
        for field in (
            "source_terms_url",
            "citation_guidance",
            "redistribution_status",
            "takedown_contact",
            "deidentification_caveat",
            "next_action",
        ):
            if not str(source.get(field, "")).strip():
                blockers.append(f"{source_id}:missing_{field}")
        if not source.get("privacy_caveats"):
            warnings.append(f"{source_id}:missing_privacy_caveats")
    return {
        "schema_version": SOURCE_MATURITY_SCHEMA_VERSION,
        "generated_at": utc_now_iso(),
        "status": "blocked" if blockers else ("warn" if warnings else "pass"),
        "summary": {
            "source_count": len(sources),
            "unresolved_source_count": sum(
                1 for source in sources if str(source.get("status", "")) != "reviewed"
            ),
            "blocker_count": len(blockers),
            "warning_count": len(warnings),
        },
        "blockers": sorted(blockers),
        "warnings": sorted(warnings),
    }


def build_parser_risk_ledger() -> JsonObject:
    """Prioritize source-specific parser and live-smoke hardening."""
    sources = []
    for source_id, info in SOURCE_REGISTRY.items():
        high_risk = source_id in HIGH_RISK_GENERIC_PARSER_SOURCES
        sources.append(
            {
                "source_id": source_id,
                "name": info["name"],
                "url": info.get("url", ""),
                "risk": "high" if high_risk else "review",
                "generic_parser_replacement_required": high_risk,
                "proof_status": "source_specific_parser_required"
                if high_risk
                else "selector_drift_review_required",
                "promotion_gate": "source_specific_parser_proof"
                if high_risk
                else "live_selector_drift_smoke_pass",
                "fixture_requirements": [
                    "pagination",
                    "detail page",
                    "PDF or document asset",
                    "missing or corrected date",
                    "source-specific identifier",
                ],
                "live_smoke_checks": {
                    "reachability": "required",
                    "selector_drift": "required",
                    "robots_or_terms_posture": "required",
                    "full_backfill_in_default_ci": False,
                },
                "next_action": (
                    "replace generic listing extraction with source-specific parser proof."
                    if high_risk
                    else "review whether generic parser remains acceptable for live site shape."
                ),
            }
        )
    return {
        "schema_version": SOURCE_MATURITY_SCHEMA_VERSION,
        "generated_at": utc_now_iso(),
        "status": "action_required",
        "high_risk_source_count": sum(
            1 for source in sources if source["generic_parser_replacement_required"]
        ),
        "sources": sources,
    }


def build_corpus_completion_readiness(
    *,
    source_completeness: Mapping[str, Any],
    source_rights_review: Mapping[str, Any],
    parser_risk: Mapping[str, Any],
    source_discovery_queue: Mapping[str, Any],
    source_verification: Mapping[str, Any],
    strict: bool = False,
) -> JsonObject:
    """Build release-gating evidence for complete-corpus claims."""
    blockers: list[str] = []
    warnings: list[str] = []
    if source_completeness.get("status") != "pass":
        blockers.append("source_completeness_unresolved")
    rights_validation = validate_source_rights_review_ledger(source_rights_review)
    if rights_validation["status"] != "pass":
        blockers.append("rights_review_unresolved")
    high_risk_unresolved = [
        str(source.get("source_id"))
        for source in parser_risk.get("sources", [])
        if isinstance(source, Mapping)
        and source.get("generic_parser_replacement_required")
        and source.get("proof_status") != "source_specific_parser_proven"
    ]
    if high_risk_unresolved:
        blockers.append("parser_replacement_unresolved")
    unpromoted_candidates = [
        str(candidate.get("candidate_id"))
        for candidate in source_discovery_queue.get("candidates", [])
        if isinstance(candidate, Mapping)
        and candidate.get("decision") == "approved"
        and candidate.get("promotion_status") != "ready_for_canonical_release"
    ]
    if unpromoted_candidates:
        blockers.append("candidate_sources_unpromoted")
    reconciliation = source_verification.get("reconciliation", {})
    summary = reconciliation.get("summary", {}) if isinstance(reconciliation, Mapping) else {}
    unresolved_counts = {
        "missing_count": int(summary.get("missing_count", 0) or 0),
        "extra_count": int(summary.get("extra_count", 0) or 0),
        "duplicate_count": int(summary.get("duplicate_count", 0) or 0),
        "ambiguous_count": int(summary.get("ambiguous_count", 0) or 0),
    }
    if source_verification.get("status") == "blocked" or any(unresolved_counts.values()):
        blockers.append("source_verification_unresolved")
    if not strict and blockers:
        warnings.extend(blockers)
    return {
        "schema_version": SOURCE_MATURITY_SCHEMA_VERSION,
        "generated_at": utc_now_iso(),
        "status": "blocked" if blockers and strict else ("warn" if blockers else "pass"),
        "strict": strict,
        "blockers": sorted(set(blockers)) if strict else [],
        "warnings": sorted(set(warnings)),
        "rights_validation": rights_validation,
        "high_risk_parser_sources": sorted(high_risk_unresolved),
        "unpromoted_candidate_sources": sorted(unpromoted_candidates),
        "source_verification_unresolved_counts": unresolved_counts,
    }


def build_publication_governance_ledger() -> JsonObject:
    """Record mirror, publication, and project-governance gates."""
    items = [
        {
            "id": "github_mirror_secrets",
            "status": "gated",
            "surface": "GitHub Actions secrets",
            "required_evidence": "public GitLab and Codeberg mirror workflow readback.",
        },
        {
            "id": "osf_activation",
            "status": "inactive_by_policy",
            "surface": "OSF",
            "required_evidence": "dedicated mirror activation policy before upload.",
        },
        {
            "id": "zenodo_production_doi",
            "status": "protected_manual_handoff",
            "surface": "Zenodo",
            "required_evidence": "human approval after draft evidence review.",
        },
        {
            "id": "riopa_mirror_source_option",
            "status": "documented_api_fallback",
            "surface": "GitHub Projects/RIOPA",
            "required_evidence": "dedicated project option or documented fallback to other.",
        },
        {
            "id": "post_expansion_monthly_publication",
            "status": "required",
            "surface": "GitHub, Hugging Face, Zenodo",
            "required_evidence": "same manifest hash across release assets and remote readback.",
        },
    ]
    return {
        "schema_version": SOURCE_MATURITY_SCHEMA_VERSION,
        "generated_at": utc_now_iso(),
        "status": "gated",
        "items": items,
    }


def build_backfill_run_manifest(
    records: Iterable[Mapping[str, Any]],
    *,
    run_id: str = "local-fixture-proof",
) -> JsonObject:
    """Build an idempotent run manifest with raw provenance fields."""
    entries = []
    seen_assets: set[str] = set()
    for record in records:
        metadata = _metadata(record)
        url = str(record.get("url") or metadata.get("url") or "")
        raw_sha256 = str(metadata.get("raw_sha256") or "")
        asset_key = raw_sha256 or hashlib.sha256(url.encode("utf-8")).hexdigest()
        seen_assets.add(asset_key)
        entries.append(
            {
                "record_id": _record_id(record),
                "source_id": str(record.get("source", "")),
                "canonical_url": url,
                "retrieved_at": str(metadata.get("retrieved_at", "")),
                "http_status": int(metadata.get("http_status", 200) or 200),
                "content_type": str(metadata.get("content_type", "text/html")),
                "etag": str(metadata.get("etag", "")),
                "last_modified": str(metadata.get("last_modified", "")),
                "raw_sha256": raw_sha256,
                "parser_name": str(metadata.get("parser_name", "")),
                "parser_version": str(metadata.get("parser_version", "")),
                "derived_text_sha256": hashlib.sha256(
                    str(record.get("text", "")).encode("utf-8")
                ).hexdigest(),
                "host": urlparse(url).netloc,
            }
        )
    return {
        "schema_version": SOURCE_MATURITY_SCHEMA_VERSION,
        "generated_at": utc_now_iso(),
        "run_id": run_id,
        "status": "complete",
        "checkpoint": {
            "cursor": "",
            "record_count": len(entries),
            "raw_asset_count": len(seen_assets),
        },
        "politeness": {
            "retry_backoff": "configured-per-source",
            "rate_limit": "polite-default",
            "cache_aware": True,
        },
        "records": sorted(entries, key=lambda item: (item["source_id"], item["record_id"])),
    }


def build_deduplication_ledger(records: Iterable[Mapping[str, Any]]) -> JsonObject:
    """Detect duplicate record IDs, URLs, and content hashes."""
    record_ids: Counter[str] = Counter()
    urls: Counter[str] = Counter()
    text_hashes: Counter[str] = Counter()
    aliases: dict[str, list[str]] = defaultdict(list)
    for record in records:
        record_id = _record_id(record)
        url = str(record.get("url") or _metadata(record).get("url") or "")
        text_hash = hashlib.sha256(str(record.get("text", "")).encode("utf-8")).hexdigest()
        if record_id:
            record_ids[record_id] += 1
        if url:
            urls[url] += 1
        if str(record.get("text", "")).strip():
            text_hashes[text_hash] += 1
            aliases[text_hash].append(record_id)
    duplicates = {
        "record_ids": sorted(item for item, count in record_ids.items() if count > 1),
        "urls": sorted(item for item, count in urls.items() if count > 1),
        "content_hashes": sorted(item for item, count in text_hashes.items() if count > 1),
    }
    return {
        "schema_version": SOURCE_MATURITY_SCHEMA_VERSION,
        "generated_at": utc_now_iso(),
        "status": "warn" if any(duplicates.values()) else "pass",
        "duplicates": duplicates,
        "canonical_aliases": {
            digest: ids for digest, ids in sorted(aliases.items()) if len(ids) > 1
        },
    }


def build_freshness_slo_ledger(
    maturity_ledger: Mapping[str, Any],
    *,
    max_unknown_days: int = 90,
) -> JsonObject:
    """Build conservative source freshness SLO evidence."""
    sources = []
    for source in maturity_ledger.get("sources", []):
        if not isinstance(source, Mapping):
            continue
        last_crawl = str(source.get("last_successful_crawl_at", ""))
        status = "unknown" if not last_crawl else "observed"
        sources.append(
            {
                "source_id": source.get("source_id", ""),
                "status": status,
                "last_successful_crawl_at": last_crawl,
                "max_unknown_days": max_unknown_days,
                "issue_required": status == "unknown",
            }
        )
    return {
        "schema_version": SOURCE_MATURITY_SCHEMA_VERSION,
        "generated_at": utc_now_iso(),
        "status": "warn" if any(source["issue_required"] for source in sources) else "pass",
        "sources": sources,
    }


def validate_public_claims(
    claims: Mapping[str, Any] | str,
    *,
    source_maturity: Mapping[str, Any],
    strict: bool = False,
) -> list[str]:
    """Validate that public prose does not overclaim historical completeness."""
    if isinstance(claims, str):
        texts = {"text": claims}
    else:
        markdown = claims.get("markdown", {}) if isinstance(claims, Mapping) else {}
        texts = markdown if isinstance(markdown, Mapping) else {}
    all_complete = bool(
        source_maturity.get("summary", {}).get("all_sources_historically_complete", False)
    )
    failures: list[str] = []
    for name, text in texts.items():
        lowered = str(text).lower()
        if (
            any(pattern in lowered for pattern in PUBLIC_CLAIM_OVERSTATEMENT_PATTERNS)
            and not all_complete
        ):
            failures.append(
                f"{name} overclaims historical completeness without source maturity proof."
            )
    if strict and not all_complete:
        failures.append("strict public claims require all sources to be historically complete.")
    return failures
