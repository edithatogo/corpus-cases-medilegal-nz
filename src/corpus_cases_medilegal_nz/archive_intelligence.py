"""Archive maturity scoring and intelligence reports."""

from __future__ import annotations

import json
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from corpus_cases_medilegal_nz.archive import utc_now_iso, write_json

JsonObject = dict[str, Any]

ARCHIVE_INTELLIGENCE_SCHEMA_VERSION = "1.0.0"


@dataclass(frozen=True)
class MaturityDimension:
    """Weighted archive maturity dimension."""

    dimension_id: str
    label: str
    weight: int
    rationale: str


MATURITY_DIMENSIONS: tuple[MaturityDimension, ...] = (
    MaturityDimension(
        dimension_id="release_evidence_completeness",
        label="Release evidence completeness",
        weight=15,
        rationale="Canonical release evidence must carry version, git, checksums, quality, and ledgers.",
    ),
    MaturityDimension(
        dimension_id="source_coverage_completeness",
        label="Source coverage completeness",
        weight=15,
        rationale="Coverage claims must be source-specific and backed by configured source states.",
    ),
    MaturityDimension(
        dimension_id="collection_and_parsing_progress",
        label="Collection and parsing progress",
        weight=15,
        rationale="Parser-complete sources need non-zero validated records and quality-gate status.",
    ),
    MaturityDimension(
        dimension_id="metadata_package_completeness",
        label="Metadata package completeness",
        weight=15,
        rationale="Discovery surfaces need complete Croissant, RO-Crate, Frictionless, DCAT, PROV-O, DataCite, schema.org, and Hugging Face metadata.",
    ),
    MaturityDimension(
        dimension_id="public_surface_consistency",
        label="Public-surface consistency",
        weight=10,
        rationale="GitHub, Hugging Face, Zenodo, and optional mirrors must match their evidence-backed states.",
    ),
    MaturityDimension(
        dimension_id="security_and_provenance_posture",
        label="Security and provenance posture",
        weight=15,
        rationale="Attestations, SBOMs, legal provenance, and quality gates protect the release chain.",
    ),
    MaturityDimension(
        dimension_id="remote_publication_proof",
        label="Remote publication proof",
        weight=15,
        rationale="Mutable and immutable publication surfaces need readback or protected handoff proof.",
    ),
)

REQUIRED_RELEASE_EVIDENCE_KEYS = {
    "release",
    "git",
    "checksums",
    "quality",
    "source_coverage",
    "source_collection_audit",
    "collection_quality_gates",
    "public_surface",
    "legal_provenance",
    "attestation_verification",
}

REQUIRED_METADATA_PACKAGES = {
    "croissant.jsonld",
    "ro-crate-metadata.json",
    "datapackage.json",
    "dcat.jsonld",
    "prov-o.jsonld",
    "datacite.json",
    "schema-org-dataset.jsonld",
    "huggingface-dataset-card-metadata.json",
}


def severity_for_score(score: float) -> str:
    """Return a deterministic maturity severity for a 0-100 score."""
    if score >= 90:
        return "leading"
    if score >= 75:
        return "strong"
    if score >= 60:
        return "developing"
    if score >= 40:
        return "fragile"
    return "blocked"


def _ratio_score(passed: int, total: int) -> int:
    if total <= 0:
        return 0
    return round((passed / total) * 100)


def _dimension_result(
    dimension: MaturityDimension,
    score: int,
    explanation: str,
    evidence: Mapping[str, Any],
) -> JsonObject:
    return {
        "id": dimension.dimension_id,
        "label": dimension.label,
        "weight": dimension.weight,
        "score": max(0, min(100, score)),
        "severity": severity_for_score(score),
        "explanation": explanation,
        "rationale": dimension.rationale,
        "evidence": dict(evidence),
    }


def _score_release_evidence(evidence: Mapping[str, Any]) -> JsonObject:
    dimension = MATURITY_DIMENSIONS[0]
    present = sorted(REQUIRED_RELEASE_EVIDENCE_KEYS.intersection(evidence))
    missing = sorted(REQUIRED_RELEASE_EVIDENCE_KEYS.difference(evidence))
    score = _ratio_score(len(present), len(REQUIRED_RELEASE_EVIDENCE_KEYS))
    if missing:
        explanation = f"Release evidence is missing {len(missing)} required key(s)."
    else:
        explanation = "Release evidence contains all required archive-family keys."
    return _dimension_result(
        dimension,
        score,
        explanation,
        {"present_keys": present, "missing_keys": missing},
    )


def _score_source_coverage(evidence: Mapping[str, Any]) -> JsonObject:
    dimension = MATURITY_DIMENSIONS[1]
    coverage = evidence.get("source_coverage", {})
    sources = coverage.get("sources", []) if isinstance(coverage, Mapping) else []
    if not isinstance(sources, Sequence):
        sources = []
    source_count = len(sources)
    backed_sources = [
        source
        for source in sources
        if isinstance(source, Mapping)
        and source.get("config_exists")
        and source.get("status") in {"active", "configured", "stub/planned"}
    ]
    validated_sources = [
        source
        for source in sources
        if isinstance(source, Mapping) and int(source.get("record_count", 0) or 0) > 0
    ]
    base_score = _ratio_score(len(backed_sources), source_count)
    validated_bonus = min(20, len(validated_sources) * 4)
    score = min(100, base_score + validated_bonus)
    explanation = (
        f"{len(backed_sources)}/{source_count} configured sources have evidence-backed coverage; "
        f"{len(validated_sources)} source(s) have local records."
    )
    return _dimension_result(
        dimension,
        score,
        explanation,
        {
            "source_count": source_count,
            "evidence_backed_source_count": len(backed_sources),
            "validated_source_count": len(validated_sources),
        },
    )


def _score_collection_and_parsing(evidence: Mapping[str, Any]) -> JsonObject:
    dimension = MATURITY_DIMENSIONS[2]
    gates = evidence.get("collection_quality_gates", {})
    audit = evidence.get("source_collection_audit", {})
    gate_status = gates.get("status") if isinstance(gates, Mapping) else None
    summaries = gates.get("source_validation_summaries", []) if isinstance(gates, Mapping) else []
    stage_counts = audit.get("stage_counts", {}) if isinstance(audit, Mapping) else {}
    if not isinstance(summaries, Sequence):
        summaries = []
    complete_count = sum(
        1
        for summary in summaries
        if isinstance(summary, Mapping)
        and summary.get("parser_complete") is True
        and int(summary.get("record_count", 0) or 0) > 0
        and summary.get("status") == "pass"
    )
    parser_complete_count = sum(
        1
        for summary in summaries
        if isinstance(summary, Mapping) and summary.get("parser_complete")
    )
    score = _ratio_score(complete_count, parser_complete_count)
    if gate_status == "blocked":
        score = min(score, 39)
    explanation = (
        f"{complete_count}/{parser_complete_count} parser-complete source(s) have non-zero "
        f"records and passing quality gates."
    )
    return _dimension_result(
        dimension,
        score,
        explanation,
        {
            "collection_quality_status": gate_status,
            "parser_complete_source_count": parser_complete_count,
            "validated_parser_complete_source_count": complete_count,
            "stage_counts": dict(stage_counts) if isinstance(stage_counts, Mapping) else {},
        },
    )


def _score_metadata_packages(evidence: Mapping[str, Any]) -> JsonObject:
    dimension = MATURITY_DIMENSIONS[3]
    metadata = evidence.get("metadata_packages", evidence.get("metadata_package_manifest", {}))
    packages = metadata.get("packages", []) if isinstance(metadata, Mapping) else []
    package_names = {
        Path(str(package.get("path", ""))).name
        for package in packages
        if isinstance(package, Mapping)
    }
    present = sorted(REQUIRED_METADATA_PACKAGES.intersection(package_names))
    missing = sorted(REQUIRED_METADATA_PACKAGES.difference(package_names))
    score = _ratio_score(len(present), len(REQUIRED_METADATA_PACKAGES))
    explanation = (
        f"{len(present)}/{len(REQUIRED_METADATA_PACKAGES)} required metadata packages are present."
    )
    return _dimension_result(
        dimension,
        score,
        explanation,
        {"present_packages": present, "missing_packages": missing},
    )


def _score_public_surface(evidence: Mapping[str, Any]) -> JsonObject:
    dimension = MATURITY_DIMENSIONS[4]
    public_surface = evidence.get("public_surface", {})
    surfaces = public_surface.get("surfaces", {}) if isinstance(public_surface, Mapping) else {}
    if not isinstance(surfaces, Mapping):
        surfaces = {}
    expected = {"github", "hugging_face", "zenodo", "osf", "future_metadata"}
    present = expected.intersection(surfaces)
    inconsistent = [
        surface_id
        for surface_id, surface in surfaces.items()
        if isinstance(surface, Mapping) and not surface.get("status")
    ]
    score = _ratio_score(len(present) - len(inconsistent), len(expected))
    explanation = (
        f"{len(present)}/{len(expected)} expected public surfaces are represented with "
        f"{len(inconsistent)} status gap(s)."
    )
    return _dimension_result(
        dimension,
        score,
        explanation,
        {"present_surfaces": sorted(present), "status_gaps": sorted(inconsistent)},
    )


def _score_security_and_provenance(evidence: Mapping[str, Any]) -> JsonObject:
    dimension = MATURITY_DIMENSIONS[5]
    checks = {
        "legal_provenance": bool(evidence.get("legal_provenance")),
        "attestation_verification": bool(evidence.get("attestation_verification")),
        "quality_no_blockers": int(
            evidence.get("quality", {}).get("blocking_issue_count", 1)
            if isinstance(evidence.get("quality"), Mapping)
            else 1
        )
        == 0,
        "collection_gates_pass": evidence.get("collection_quality_gates", {}).get("status")
        == "pass"
        if isinstance(evidence.get("collection_quality_gates"), Mapping)
        else False,
        "checksum_manifest": bool(evidence.get("checksums", {}).get("manifest_path"))
        if isinstance(evidence.get("checksums"), Mapping)
        else False,
    }
    passed = [check for check, ok in checks.items() if ok]
    failed = [check for check, ok in checks.items() if not ok]
    score = _ratio_score(len(passed), len(checks))
    explanation = f"{len(passed)}/{len(checks)} security and provenance checks pass."
    return _dimension_result(
        dimension,
        score,
        explanation,
        {"passed_checks": sorted(passed), "failed_checks": sorted(failed)},
    )


def _score_remote_publication(evidence: Mapping[str, Any]) -> JsonObject:
    dimension = MATURITY_DIMENSIONS[6]
    release = evidence.get("release", {}) if isinstance(evidence.get("release"), Mapping) else {}
    hf = (
        evidence.get("hugging_face", {})
        if isinstance(evidence.get("hugging_face"), Mapping)
        else {}
    )
    zenodo = evidence.get("zenodo", {}) if isinstance(evidence.get("zenodo"), Mapping) else {}
    checks = {
        "github_release_url": bool(release.get("github_release_url")),
        "hugging_face_revision": bool(hf.get("revision")),
        "hugging_face_manifest_verified": hf.get("remote_manifest_verified") is True,
        "zenodo_draft_or_record": bool(zenodo.get("draft_id") or zenodo.get("record_url")),
        "zenodo_protected_handoff": zenodo.get("publish_handoff_only") is True,
    }
    passed = [check for check, ok in checks.items() if ok]
    failed = [check for check, ok in checks.items() if not ok]
    score = _ratio_score(len(passed), len(checks))
    explanation = f"{len(passed)}/{len(checks)} remote publication proof checks pass."
    return _dimension_result(
        dimension,
        score,
        explanation,
        {"passed_checks": sorted(passed), "failed_checks": sorted(failed)},
    )


SCORERS = (
    _score_release_evidence,
    _score_source_coverage,
    _score_collection_and_parsing,
    _score_metadata_packages,
    _score_public_surface,
    _score_security_and_provenance,
    _score_remote_publication,
)


def build_archive_maturity_report(evidence: Mapping[str, Any]) -> JsonObject:
    """Build a weighted archive maturity report from release evidence."""
    dimensions = [scorer(evidence) for scorer in SCORERS]
    weighted_score = round(
        sum(float(item["score"]) * int(item["weight"]) for item in dimensions)
        / sum(dimension.weight for dimension in MATURITY_DIMENSIONS),
        2,
    )
    blockers = [
        item["id"]
        for item in dimensions
        if item["severity"] in {"blocked", "fragile"} and item["score"] < 60
    ]
    return {
        "schema_version": ARCHIVE_INTELLIGENCE_SCHEMA_VERSION,
        "generated_at": utc_now_iso(),
        "model": {
            "id": "medilegal-archive-maturity",
            "version": "1.0.0",
            "score_range": "0-100",
            "severity_levels": {
                "leading": "90-100: strong automation, evidence, publication proof, and governance.",
                "strong": "75-89: release-ready with bounded improvement areas.",
                "developing": "60-74: usable evidence exists but notable maturity gaps remain.",
                "fragile": "40-59: publication claims need caution and follow-up.",
                "blocked": "0-39: release or public claims are blocked by missing evidence.",
            },
        },
        "score": weighted_score,
        "severity": severity_for_score(weighted_score),
        "blocking_dimensions": blockers,
        "dimensions": dimensions,
    }


def build_archive_intelligence_from_file(release_evidence_path: Path) -> JsonObject:
    """Load release evidence and build archive maturity intelligence."""
    evidence = json.loads(release_evidence_path.read_text(encoding="utf-8-sig"))
    if not isinstance(evidence, Mapping):
        raise ValueError("release evidence must be a JSON object")
    enriched_evidence = dict(evidence)
    if "metadata_packages" not in enriched_evidence:
        metadata_path = (
            release_evidence_path.parent.parent / "metadata" / "metadata_packages_manifest.json"
        )
        if metadata_path.is_file():
            enriched_evidence["metadata_packages"] = json.loads(
                metadata_path.read_text(encoding="utf-8-sig")
            )
    return build_archive_maturity_report(enriched_evidence)


def write_archive_intelligence_report(
    release_evidence_path: Path,
    output_path: Path,
) -> JsonObject:
    """Write archive maturity intelligence derived from release evidence."""
    report = build_archive_intelligence_from_file(release_evidence_path)
    write_json(output_path, report)
    return report
