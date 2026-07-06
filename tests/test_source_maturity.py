from __future__ import annotations

from pathlib import Path

from corpus_cases_medilegal_nz.collection_proof import build_fixture_collection_records
from corpus_cases_medilegal_nz.source_maturity import (
    build_candidate_coverage_report,
    SOURCE_MATURITY_LADDER,
    build_backfill_run_manifest,
    build_corpus_completion_readiness,
    build_deduplication_ledger,
    build_freshness_slo_ledger,
    build_parser_risk_ledger,
    build_publication_governance_ledger,
    build_redundant_source_validation_ledger,
    build_source_completeness_ledger,
    build_source_discovery_queue,
    build_source_maturity_ledger,
    build_source_rights_review_ledger,
    validate_public_claims,
    validate_source_rights_review_ledger,
)

ROOT = Path(__file__).resolve().parents[1]


def test_fixture_validated_records_do_not_claim_historical_completion() -> None:
    records = build_fixture_collection_records()

    ledger = build_source_maturity_ledger(root=ROOT, records=records)

    assert ledger["maturity_ladder"] == SOURCE_MATURITY_LADDER
    assert ledger["summary"]["source_count"] == 13
    assert ledger["summary"]["historically_complete_source_count"] == 0
    assert ledger["summary"]["all_sources_historically_complete"] is False
    assert ledger["summary"]["sources_with_known_targets"] == 13
    assert ledger["summary"]["total_expected_records_for_known_targets"] == 26
    assert ledger["summary"]["total_records_against_known_targets"] == 26
    assert ledger["summary"]["total_remaining_to_known_targets"] == 0
    assert ledger["summary"]["stage_counts"] == {"historical_backfill_in_progress": 13}
    hdc = next(source for source in ledger["sources"] if source["source_id"] == "hdc")
    assert hdc["parser_stage"] == "validated_records"
    assert hdc["historical_maturity_stage"] == "historical_backfill_in_progress"
    assert hdc["target"]["expected_count_confidence"] == "baseline_minimum"
    assert hdc["target_progress"] == {
        "expected_count": 2,
        "record_count": 2,
        "remaining_to_target": 0,
        "progress_ratio": 1.0,
    }


def test_known_target_can_promote_source_to_historical_completion() -> None:
    records = [record for record in build_fixture_collection_records() if record["source"] == "hdc"]

    ledger = build_source_maturity_ledger(
        root=ROOT,
        records=records,
        target_metadata={
            "sources": {
                "hdc": {
                    "expected_count": 1,
                    "expected_count_confidence": "verified",
                    "source_update_cadence": "monthly",
                    "known_limitations": [],
                }
            }
        },
        publication_manifest_hash="abc123",
    )
    hdc = next(source for source in ledger["sources"] if source["source_id"] == "hdc")

    assert hdc["historical_maturity_stage"] == "publication_evidence_current"
    assert hdc["publication_manifest_sha256"] == "abc123"


def test_source_completeness_warns_until_all_sources_are_complete() -> None:
    records = build_fixture_collection_records()

    completeness = build_source_completeness_ledger(root=ROOT, records=records)

    assert completeness["status"] == "warn"
    assert len(completeness["blockers"]) == 13
    assert "hdc is historical_backfill_in_progress" in completeness["blockers"]


def test_public_claim_validation_blocks_overbroad_historical_claims() -> None:
    records = build_fixture_collection_records()
    maturity = build_source_maturity_ledger(root=ROOT, records=records)

    failures = validate_public_claims(
        {"markdown": {"README.md": "All cases archived for every registered source."}},
        source_maturity=maturity,
        strict=True,
    )

    assert failures == [
        "README.md overclaims historical completeness without source maturity proof.",
        "strict public claims require all sources to be historically complete.",
    ]


def test_source_discovery_queue_is_review_gated() -> None:
    queue = build_source_discovery_queue()

    assert queue["status"] == "triaged"
    assert "Approved candidates are not active registry sources" in queue["promotion_policy"]
    candidate_ids = {candidate["candidate_id"] for candidate in queue["candidates"]}
    assert "acc_appeals_reviews" in candidate_ids
    assert "social_security_appeal_authority" in candidate_ids
    assert "mental_health_review_tribunal" in candidate_ids
    assert "nzlii_health_privacy_discipline" in candidate_ids
    assert "immigration_and_protection_tribunal" in candidate_ids
    assert "lawyers_conveyancers_disciplinary_tribunal" in candidate_ids


def test_source_rights_review_defaults_are_conservative() -> None:
    ledger = build_source_rights_review_ledger()

    assert ledger["status"] == "reviewed_with_caveats"
    assert len(ledger["sources"]) == 13
    assert {source["status"] for source in ledger["sources"]} == {"reviewed"}
    assert all(
        source["redistribution_status"]
        == "public-source-citation-and-derived-metadata-with-caveats"
        for source in ledger["sources"]
    )
    assert all(source["source_terms_url"] for source in ledger["sources"])
    assert all(source["next_action"] for source in ledger["sources"])


def test_source_rights_review_validation_reports_unresolved_sources() -> None:
    ledger = build_source_rights_review_ledger()

    validation = validate_source_rights_review_ledger(ledger)

    assert validation["status"] == "pass"
    assert validation["summary"]["source_count"] == 13
    assert validation["summary"]["unresolved_source_count"] == 0
    assert validation["blockers"] == []


def test_parser_risk_ledger_prioritizes_generic_parser_replacement() -> None:
    ledger = build_parser_risk_ledger()
    by_source = {source["source_id"]: source for source in ledger["sources"]}

    assert ledger["status"] == "action_required"
    assert ledger["high_risk_source_count"] == 7
    assert by_source["moj_courts"]["generic_parser_replacement_required"] is True
    assert by_source["hdc"]["generic_parser_replacement_required"] is False
    assert by_source["moj_courts"]["live_smoke_checks"]["full_backfill_in_default_ci"] is False
    assert by_source["moj_courts"]["proof_status"] == "source_specific_parser_proven"
    assert by_source["hdc"]["proof_status"] == "selector_drift_review_required"
    assert by_source["hdc"]["selector_drift_review"]["required_checks"] == [
        "reachability",
        "selector_drift",
        "robots_or_terms_posture",
    ]


def test_candidate_source_triage_records_durable_decisions() -> None:
    queue = build_source_discovery_queue()
    candidates = {candidate["candidate_id"]: candidate for candidate in queue["candidates"]}

    assert queue["status"] == "triaged"
    assert {candidate["decision"] for candidate in queue["candidates"]} == {
        "approved",
        "deferred",
        "excluded",
    }
    assert candidates["acc_appeals_reviews"]["decision"] == "approved"
    assert candidates["social_security_appeal_authority"]["decision"] == "approved"
    assert candidates["mental_health_review_tribunal"]["decision"] == "approved"
    assert candidates["nzlii_health_privacy_discipline"]["decision"] == "approved"
    assert candidates["nzlii_health_privacy_discipline"]["promotion_status"] == (
        "ready_for_canonical_implementation"
    )
    assert candidates["nzlii_health_privacy_discipline"]["promotion_scaffold"]["config"] == (
        "config/candidates/nzlii_health_privacy_discipline_pipeline.yaml"
    )
    assert candidates["acc_appeals_reviews"]["promotion_scaffold"]["config"] == (
        "config/candidates/acc_appeals_reviews_pipeline.yaml"
    )
    assert candidates["social_security_appeal_authority"]["promotion_scaffold"]["config"] == (
        "config/candidates/social_security_appeal_authority_pipeline.yaml"
    )
    assert candidates["mental_health_review_tribunal"]["promotion_scaffold"]["config"] == (
        "config/candidates/mental_health_review_tribunal_pipeline.yaml"
    )


def test_candidate_coverage_report_tracks_approved_and_excluded_families() -> None:
    queue = build_source_discovery_queue()
    redundant = build_redundant_source_validation_ledger()

    coverage = build_candidate_coverage_report(
        discovery_queue=queue,
        redundant_source_validation=redundant,
    )

    assert coverage["summary"]["approved_candidate_count"] == 4
    assert coverage["summary"]["deferred_candidate_count"] == 2
    assert coverage["summary"]["excluded_candidate_count"] == 2
    assert coverage["summary"]["approved_candidate_with_witness_count"] == 4
    assert coverage["candidate_witness_gaps"] == []


def test_redundant_source_validation_ledger_tracks_validation_witnesses() -> None:
    ledger = build_redundant_source_validation_ledger()

    assert ledger["status"] == "warn"
    assert ledger["summary"]["validation_source_count"] >= 4
    assert ledger["summary"]["missing_witness_source_count"] >= 1
    assert ledger["source_witness_counts"]["hpdt"] >= 1
    assert "hdc" in ledger["source_witnesses"]


def test_corpus_completion_readiness_blocks_complete_claims_until_all_gates_pass() -> None:
    records = build_fixture_collection_records()
    verification = {
        "status": "verified_complete",
        "reconciliation": {
            "summary": {
                "missing_count": 0,
                "extra_count": 0,
                "duplicate_count": 0,
                "ambiguous_count": 0,
            }
        },
    }

    readiness = build_corpus_completion_readiness(
        source_completeness=build_source_completeness_ledger(root=ROOT, records=records),
        source_rights_review=build_source_rights_review_ledger(),
        parser_risk=build_parser_risk_ledger(),
        source_discovery_queue=build_source_discovery_queue(),
        source_verification=verification,
        strict=True,
    )

    assert readiness["status"] == "blocked"
    assert "source_completeness_unresolved" in readiness["blockers"]
    assert "rights_review_unresolved" not in readiness["blockers"]
    assert "parser_replacement_unresolved" not in readiness["blockers"]
    assert "candidate_sources_unpromoted" not in readiness["blockers"]


def test_publication_governance_ledger_tracks_remaining_external_gates() -> None:
    ledger = build_publication_governance_ledger()
    items = {item["id"]: item for item in ledger["items"]}

    assert ledger["status"] == "gated"
    assert items["github_mirror_secrets"]["status"] == "gated"
    assert items["osf_activation"]["status"] == "inactive_by_policy"
    assert items["zenodo_production_doi"]["status"] == "protected_manual_handoff"
    assert items["riopa_mirror_source_option"]["status"] == "documented_api_fallback"


def test_backfill_manifest_captures_raw_provenance_and_text_hashes() -> None:
    records = build_fixture_collection_records()

    manifest = build_backfill_run_manifest(records)

    assert manifest["status"] == "complete"
    assert manifest["checkpoint"]["record_count"] == 26
    assert manifest["checkpoint"]["raw_asset_count"] == 13
    first = manifest["records"][0]
    assert first["canonical_url"].startswith("https://")
    assert first["derived_text_sha256"]
    assert first["parser_version"] == "1.0.0"


def test_deduplication_and_freshness_ledgers_are_deterministic() -> None:
    records = build_fixture_collection_records()
    dedupe = build_deduplication_ledger(records)
    maturity = build_source_maturity_ledger(root=ROOT, records=records)
    freshness = build_freshness_slo_ledger(maturity)

    assert dedupe["status"] == "pass"
    assert dedupe["duplicates"] == {"record_ids": [], "urls": [], "content_hashes": []}
    assert freshness["status"] == "pass"
    assert all(source["status"] == "observed" for source in freshness["sources"])
