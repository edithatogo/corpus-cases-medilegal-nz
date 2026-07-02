"""Archive maturity scoring and intelligence reports."""

from __future__ import annotations

import json
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from corpus_cases_medilegal_nz.archive import (
    build_source_collection_audit,
    build_source_coverage,
    utc_now_iso,
    write_json,
)
from corpus_cases_medilegal_nz.sources import SOURCE_REGISTRY

JsonObject = dict[str, Any]

ARCHIVE_INTELLIGENCE_SCHEMA_VERSION = "1.0.0"
ARTIFACT_MANIFEST_DIRNAME = "manifests"
HUGGINGFACE_EVIDENCE_FILENAME = "huggingface_publish_evidence.json"
GITHUB_RELEASE_EVIDENCE_FILENAME = "github_release_evidence.json"
ZENODO_EVIDENCE_FILENAME = "zenodo_draft_evidence.json"


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

CORE_OBSERVABILITY_SOURCE_IDS = {"hdc", "hpdt", "moj_tribunals", "era", "teachers"}


def _load_json_object(path: Path) -> JsonObject | None:
    """Load a JSON object if the path exists."""
    if not path.is_file():
        return None
    payload = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(payload, Mapping):
        raise ValueError(f"{path} must contain a JSON object")
    return dict(payload)


def _load_json_records(path: Path) -> list[JsonObject]:
    """Load a JSONL record set if present."""
    if not path.is_file():
        return []
    records: list[JsonObject] = []
    for line in path.read_text(encoding="utf-8-sig").splitlines():
        line = line.strip()
        if not line:
            continue
        loaded = json.loads(line)
        if isinstance(loaded, Mapping):
            records.append(dict(loaded))
    return records


def _record_metadata(record: Mapping[str, Any]) -> Mapping[str, Any]:
    """Return record metadata as a mapping."""
    metadata = record.get("metadata", {})
    return metadata if isinstance(metadata, Mapping) else {}


def _latest_timestamp(values: Sequence[str]) -> str:
    """Return the latest ISO-8601 timestamp from a sequence."""
    parsed: list[datetime] = []
    for value in values:
        if not value:
            continue
        try:
            normalized = value[:-1] + "+00:00" if value.endswith("Z") else value
            parsed.append(datetime.fromisoformat(normalized))
        except ValueError:
            continue
    if not parsed:
        return ""
    return (
        max(parsed)
        .astimezone(UTC)
        .replace(microsecond=0)
        .isoformat()
        .replace(
            "+00:00",
            "Z",
        )
    )


def _score_status(score: int) -> str:
    """Return a coarse status for source- and privacy-oriented ledgers."""
    if score >= 90:
        return "leading"
    if score >= 75:
        return "healthy"
    if score >= 50:
        return "review"
    return "blocked"


def _merge_publication_evidence(evidence: JsonObject, artifact_dir: Path) -> JsonObject:
    """Merge publication overlays into release evidence for maturity scoring."""
    merged: JsonObject = dict(evidence)
    manifest_dir = artifact_dir / ARTIFACT_MANIFEST_DIRNAME

    github_release = _load_json_object(manifest_dir / GITHUB_RELEASE_EVIDENCE_FILENAME)
    if github_release:
        release = dict(merged.get("release", {}))
        if github_release.get("github_release_url"):
            release["github_release_url"] = github_release["github_release_url"]
        if github_release.get("github_release_tag"):
            release["github_release_tag"] = github_release["github_release_tag"]
        merged["release"] = release

    hugging_face = _load_json_object(manifest_dir / HUGGINGFACE_EVIDENCE_FILENAME)
    if hugging_face:
        merged["hugging_face"] = {
            "repo_id": hugging_face.get("repo_id", merged.get("hugging_face", {}).get("repo_id")),
            "revision": hugging_face.get("revision", ""),
            "remote_manifest_verified": hugging_face.get("remote_manifest_verified", False),
            "path_in_repo": hugging_face.get("path_in_repo", ""),
        }

    zenodo = _load_json_object(manifest_dir / ZENODO_EVIDENCE_FILENAME)
    if zenodo:
        merged["zenodo"] = {
            "draft_id": zenodo.get("deposition_id", ""),
            "record_url": zenodo.get("record_url", ""),
            "doi": zenodo.get("doi", ""),
            "concept_doi": zenodo.get("concept_doi", ""),
            "publish_handoff_only": zenodo.get("publish_handoff_only", False),
        }

    metadata = _load_json_object(artifact_dir / "metadata" / "metadata_packages_manifest.json")
    if metadata:
        merged["metadata_packages"] = metadata
    return merged


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
    artifact_dir = (
        release_evidence_path.parent.parent
        if release_evidence_path.parent.name == ARTIFACT_MANIFEST_DIRNAME
        else release_evidence_path.parent
    )
    return build_archive_maturity_report(_merge_publication_evidence(dict(evidence), artifact_dir))


def build_archive_intelligence_from_artifact_dir(artifact_dir: Path) -> JsonObject:
    """Load the monthly artifact directory and build archive maturity intelligence."""
    artifact_dir = Path(artifact_dir)
    return build_archive_intelligence_from_file(
        artifact_dir / ARTIFACT_MANIFEST_DIRNAME / "release_evidence.json"
    )


def build_source_observability_ledger(
    root: Path = Path(),
    records: Iterable[Mapping[str, Any]] = (),
    previous_records: Iterable[Mapping[str, Any]] | None = None,
) -> JsonObject:
    """Build source-level observability and drift signals."""
    root = Path(root)
    current_records = [dict(record) for record in records]
    previous_records_list = [dict(record) for record in previous_records or []]
    current_counts = {
        source_id: sum(
            1 for record in current_records if str(record.get("source", "")) == source_id
        )
        for source_id in CORE_OBSERVABILITY_SOURCE_IDS
    }
    previous_counts = {
        source_id: sum(
            1 for record in previous_records_list if str(record.get("source", "")) == source_id
        )
        for source_id in CORE_OBSERVABILITY_SOURCE_IDS
    }
    coverage = build_source_coverage(root=root, records=current_records)
    coverage_by_source = {
        str(source.get("source_id", "")): dict(source)
        for source in coverage.get("sources", [])
        if isinstance(source, Mapping)
    }
    audit = build_source_collection_audit(root=root, records=current_records)
    audit_by_source = {
        str(source.get("source_id", "")): dict(source)
        for source in audit.get("sources", [])
        if isinstance(source, Mapping)
    }
    observability_sources: list[JsonObject] = []
    status_counts: dict[str, int] = {}
    for source_id, info in SOURCE_REGISTRY.items():
        source_records = [
            record for record in current_records if str(record.get("source", "")) == source_id
        ]
        config_exists = (root / str(info.get("config", ""))).is_file()
        previous_count = previous_counts.get(source_id, 0)
        current_count = current_counts.get(source_id, 0)
        metadata_items = [_record_metadata(record) for record in source_records]
        latest_fetch = _latest_timestamp(
            [str(metadata.get("retrieved_at", "")) for metadata in metadata_items]
        )
        latest_parse = _latest_timestamp(
            [
                str(
                    metadata.get(
                        "parsed_at",
                        metadata.get("retrieved_at", ""),
                    )
                )
                for metadata in metadata_items
            ]
        )
        document_classes = sorted(
            {
                str(metadata.get("document_class", "decision"))
                for metadata in metadata_items
                if str(metadata.get("document_class", "decision")).strip()
            }
        )
        if not document_classes:
            document_classes = ["decision"]
        if config_exists and info.get("url"):
            crawlability_status = "reachable"
        elif config_exists:
            crawlability_status = "configured"
        else:
            crawlability_status = "blocked"
        parser_status = audit_by_source.get(source_id, {}).get("completion_stage", "planned")
        rights_review_state = (
            next(
                (
                    str(metadata.get("rights_review_status"))
                    for metadata in metadata_items
                    if str(metadata.get("rights_review_status", "")).strip()
                ),
                "public-source-review-required",
            )
            if source_records
            else "public-source-review-required"
        )
        drift_ratio = None
        drift_severity = "stable"
        drift_warning = ""
        if previous_count > 0:
            drift_ratio = round(((current_count - previous_count) / previous_count) * 100, 1)
            if current_count < previous_count:
                drift_severity = "drop"
                drift_warning = (
                    f"{source_id} record count dropped from {previous_count} to {current_count}."
                )
        status_counts[crawlability_status] = status_counts.get(crawlability_status, 0) + 1
        observability_sources.append(
            {
                "source_id": source_id,
                "name": info["name"],
                "crawlability": {
                    "status": crawlability_status,
                    "url": info.get("url", ""),
                    "config_exists": config_exists,
                },
                "parser_completion": {
                    "status": parser_status,
                    "validated_records": current_count,
                    "previous_validated_records": previous_count,
                },
                "timestamps": {
                    "last_fetch_at": latest_fetch,
                    "last_parse_at": latest_parse,
                },
                "drift": {
                    "current_record_count": current_count,
                    "previous_record_count": previous_count,
                    "change_percent": drift_ratio,
                    "severity": drift_severity,
                    "warning": drift_warning,
                },
                "rights": {
                    "status": rights_review_state,
                    "known_exclusions": coverage_by_source.get(source_id, {}).get(
                        "known_exclusions",
                        [],
                    ),
                },
                "document_classes": document_classes,
            }
        )
    return {
        "schema_version": ARCHIVE_INTELLIGENCE_SCHEMA_VERSION,
        "generated_at": utc_now_iso(),
        "summary": {
            "source_count": len(observability_sources),
            "crawlability_counts": dict(sorted(status_counts.items())),
            "observed_source_count": sum(
                1
                for source in observability_sources
                if source["parser_completion"]["validated_records"] > 0
            ),
        },
        "sources": observability_sources,
    }


def build_privacy_rights_scoring(evidence: Mapping[str, Any]) -> JsonObject:
    """Build a conservative privacy and rights score from evidence."""
    observability = evidence.get("source_observability", {})
    sources = observability.get("sources", []) if isinstance(observability, Mapping) else []
    active_sources = [
        source
        for source in sources
        if isinstance(source, Mapping)
        and int(source.get("parser_completion", {}).get("validated_records", 0) or 0) > 0
    ]
    relevant_sources = active_sources or [
        source for source in sources if isinstance(source, Mapping)
    ]
    scores: list[JsonObject] = []
    for source in relevant_sources:
        if not isinstance(source, Mapping):
            continue
        rights = source.get("rights", {})
        rights_status = str(rights.get("status", "public-source-review-required"))
        exclusions = rights.get("known_exclusions", [])
        if rights_status == "reviewed":
            score = 100
        elif rights_status == "public-source-review-required":
            score = 55
        elif rights_status == "blocked":
            score = 15
        else:
            score = 40
        if isinstance(exclusions, Sequence):
            score = max(0, score - min(20, len(list(exclusions)) * 5))
        scores.append(
            {
                "source_id": source.get("source_id", ""),
                "name": source.get("name", ""),
                "rights_status": rights_status,
                "known_exclusions": list(exclusions) if isinstance(exclusions, Sequence) else [],
                "score": score,
                "severity": _score_status(score),
            }
        )
    overall = round(sum(item["score"] for item in scores) / len(scores), 2) if scores else 0.0
    blockers = [item["source_id"] for item in scores if item["score"] < 50]
    return {
        "schema_version": ARCHIVE_INTELLIGENCE_SCHEMA_VERSION,
        "generated_at": utc_now_iso(),
        "status": _score_status(int(overall)),
        "score": overall,
        "blocking_sources": blockers,
        "sources": scores,
    }


def build_archive_anomaly_report(
    evidence: Mapping[str, Any],
    *,
    previous_evidence: Mapping[str, Any] | None = None,
    record_drop_threshold: float = 0.5,
) -> JsonObject:
    """Build anomaly signals for counts, schema, and publication proof."""
    observability = evidence.get("source_observability", {})
    current_sources = observability.get("sources", []) if isinstance(observability, Mapping) else []
    previous_coverage = {}
    if previous_evidence and isinstance(previous_evidence, Mapping):
        previous_coverage = {
            str(source.get("source_id", "")): dict(source)
            for source in previous_evidence.get("source_coverage", {}).get("sources", [])
            if isinstance(source, Mapping)
        }
    anomalies: list[JsonObject] = []
    for source in current_sources:
        if not isinstance(source, Mapping):
            continue
        drift = source.get("drift", {})
        change_percent = drift.get("change_percent")
        if isinstance(change_percent, (int, float)) and change_percent <= -(
            record_drop_threshold * 100
        ):
            anomalies.append(
                {
                    "type": "record_count_drop",
                    "severity": "warning",
                    "source_id": source.get("source_id", ""),
                    "message": drift.get("warning")
                    or f"{source.get('source_id')} record count dropped.",
                }
            )
        previous_url = previous_coverage.get(str(source.get("source_id", "")), {}).get("url", "")
        current_url = ""
        for coverage_source in evidence.get("source_coverage", {}).get("sources", []):
            if isinstance(coverage_source, Mapping) and coverage_source.get(
                "source_id"
            ) == source.get(
                "source_id",
            ):
                current_url = str(coverage_source.get("url", ""))
                break
        if previous_url and current_url and previous_url != current_url:
            anomalies.append(
                {
                    "type": "source_url_drift",
                    "severity": "warning",
                    "source_id": source.get("source_id", ""),
                    "message": "Source URL changed between evidence snapshots.",
                }
            )
    schema = evidence.get("schema", {}) if isinstance(evidence.get("schema"), Mapping) else {}
    schema_version = str(schema.get("record_schema_version", ""))
    if schema_version and schema_version != "1.0.0":
        anomalies.append(
            {
                "type": "schema_drift",
                "severity": "warning",
                "message": f"Record schema version {schema_version} differs from the current contract.",
            }
        )
    hf = (
        evidence.get("hugging_face", {})
        if isinstance(evidence.get("hugging_face"), Mapping)
        else {}
    )
    if hf and hf.get("remote_manifest_verified") is not True:
        anomalies.append(
            {
                "type": "remote_manifest_verification",
                "severity": "blocker",
                "message": "Hugging Face remote manifest verification is missing or false.",
            }
        )
    metadata = evidence.get("metadata_packages", {})
    package_names = (
        {
            Path(str(package.get("path", ""))).name
            for package in metadata.get("packages", [])
            if isinstance(package, Mapping)
        }
        if isinstance(metadata, Mapping)
        else set()
    )
    missing_packages = sorted(REQUIRED_METADATA_PACKAGES.difference(package_names))
    if missing_packages:
        anomalies.append(
            {
                "type": "metadata_inconsistency",
                "severity": "warning",
                "missing_packages": missing_packages,
                "message": "One or more required metadata packages are missing.",
            }
        )
    blockers = [item for item in anomalies if item["severity"] == "blocker"]
    warnings = [item for item in anomalies if item["severity"] == "warning"]
    status = "fail" if blockers else ("warn" if warnings else "pass")
    return {
        "schema_version": ARCHIVE_INTELLIGENCE_SCHEMA_VERSION,
        "generated_at": utc_now_iso(),
        "status": status,
        "thresholds": {
            "record_drop_threshold": record_drop_threshold,
        },
        "anomalies": anomalies,
        "blockers": blockers,
        "warnings": warnings,
    }


def build_public_claims(
    evidence: Mapping[str, Any], *, maturity_report: Mapping[str, Any] | None = None
) -> JsonObject:
    """Generate public claims from archive ledgers."""
    release = evidence.get("release", {}) if isinstance(evidence.get("release"), Mapping) else {}
    quality = evidence.get("quality", {}) if isinstance(evidence.get("quality"), Mapping) else {}
    coverage = (
        evidence.get("source_coverage", {})
        if isinstance(evidence.get("source_coverage"), Mapping)
        else {}
    )
    audit = (
        evidence.get("source_collection_audit", {})
        if isinstance(evidence.get("source_collection_audit"), Mapping)
        else {}
    )
    observability = (
        evidence.get("source_observability", {})
        if isinstance(evidence.get("source_observability"), Mapping)
        else {}
    )
    privacy = (
        evidence.get("privacy_rights_scoring", {})
        if isinstance(evidence.get("privacy_rights_scoring"), Mapping)
        else build_privacy_rights_scoring(evidence)
    )
    validated_sources = [
        source
        for source in audit.get("sources", [])
        if isinstance(source, Mapping) and source.get("completion_stage") == "validated_records"
    ]
    active_sources = [
        source
        for source in coverage.get("sources", [])
        if isinstance(source, Mapping) and int(source.get("record_count", 0) or 0) > 0
    ]
    public_url = release.get("github_release_url") or "pending publication"
    hf_revision = str(evidence.get("hugging_face", {}).get("revision", "") or "pending publication")
    zenodo = evidence.get("zenodo", {}) if isinstance(evidence.get("zenodo"), Mapping) else {}
    zenodo_claim = str(zenodo.get("record_url") or zenodo.get("draft_id") or "pending publication")
    maturity_score = maturity_report.get("score") if isinstance(maturity_report, Mapping) else None
    readme = (
        f"This archive currently records {quality.get('record_count', 0)} validated records "
        f"across {len(active_sources)} active sources. "
        f"Publication proof is published via GitHub release {public_url}, Hugging Face revision "
        f"{hf_revision}, and Zenodo evidence {zenodo_claim}."
    )
    dataset_card = (
        f"Coverage is sourced from {len(validated_sources)} parser-complete sources. "
        f"Quality gates report {quality.get('blocking_issue_count', 0)} blocking issue(s). "
        f"Privacy/rights status is summarized as {privacy.get('status', 'unknown')}."
    )
    release_notes = (
        f"Release maturity score: {maturity_score if maturity_score is not None else 'n/a'}. "
        f"Observability tracks {len(observability.get('sources', []))} sources and evidence-backed "
        f"claims are generated from ledgers rather than prose."
    )
    project_summary = (
        f"Project sync should reference the same release evidence used for the archive: "
        f"{release.get('github_release_tag', 'dataset release')}."
    )
    return {
        "schema_version": ARCHIVE_INTELLIGENCE_SCHEMA_VERSION,
        "generated_at": utc_now_iso(),
        "facts": {
            "record_count": quality.get("record_count", 0),
            "active_source_count": len(active_sources),
            "validated_source_count": len(validated_sources),
            "maturity_score": maturity_score,
            "privacy_status": privacy.get("status", "unknown"),
        },
        "markdown": {
            "README.md": readme,
            "dataset-card.md": dataset_card,
            "release-notes.md": release_notes,
            "github-project-summary.md": project_summary,
        },
    }


def build_federation_compatibility_report(
    evidence: Mapping[str, Any],
    *,
    profile_version: str = "1.0.0",
) -> JsonObject:
    """Check archive evidence against the shared archive-family contract."""
    required_sections = sorted(REQUIRED_RELEASE_EVIDENCE_KEYS | {"metadata_packages"})
    present_sections = sorted(
        key for key in required_sections if key in evidence and evidence.get(key) is not None
    )
    missing_sections = sorted(set(required_sections).difference(evidence))
    current_versions = {
        "release_evidence": str(evidence.get("schema_version", "")),
        "source_coverage": str(evidence.get("source_coverage", {}).get("schema_version", "")),
        "public_surface": str(evidence.get("public_surface", {}).get("schema_version", "")),
        "legal_provenance": str(evidence.get("legal_provenance", {}).get("schema_version", "")),
    }
    status = "compatible" if not missing_sections else "drift"
    return {
        "schema_version": ARCHIVE_INTELLIGENCE_SCHEMA_VERSION,
        "generated_at": utc_now_iso(),
        "profile_version": profile_version,
        "status": status,
        "present_sections": present_sections,
        "missing_sections": missing_sections,
        "version_alignment": current_versions,
        "target_repositories": [
            "corpus-cases-medilegal-nz",
            "corpus-law-nz",
            "corpus-nz-hansard",
            "fyi-archive",
            "hathi-nz",
        ],
    }


def build_archive_intelligence_bundle(
    evidence: Mapping[str, Any],
    *,
    root: Path = Path(),
    previous_evidence: Mapping[str, Any] | None = None,
) -> JsonObject:
    """Build the full archive intelligence bundle."""
    root = Path(root)
    current_records = _load_json_records(root / "data" / "processed" / "jsonl" / "records.jsonl")
    previous_records = _load_json_records(
        root / "data" / "processed" / "jsonl" / "previous_records.jsonl"
    )
    source_observability = build_source_observability_ledger(
        root=root,
        records=current_records,
        previous_records=previous_records,
    )
    enriched = dict(evidence)
    enriched["source_observability"] = source_observability
    privacy_rights_scoring = build_privacy_rights_scoring(enriched)
    enriched["privacy_rights_scoring"] = privacy_rights_scoring
    maturity = build_archive_maturity_report(enriched)
    anomaly_report = build_archive_anomaly_report(
        enriched,
        previous_evidence=previous_evidence,
    )
    public_claims = build_public_claims(enriched, maturity_report=maturity)
    federation_compatibility = build_federation_compatibility_report(enriched)
    return {
        "schema_version": ARCHIVE_INTELLIGENCE_SCHEMA_VERSION,
        "generated_at": utc_now_iso(),
        "maturity": maturity,
        "source_observability": source_observability,
        "privacy_rights_scoring": privacy_rights_scoring,
        "anomaly_report": anomaly_report,
        "public_claims": public_claims,
        "federation_compatibility": federation_compatibility,
    }


def write_archive_intelligence_bundle(
    artifact_dir: Path,
    output_dir: Path,
    *,
    root: Path = Path(),
) -> JsonObject:
    """Write the full archive intelligence bundle to disk."""
    artifact_dir = Path(artifact_dir)
    output_dir = Path(output_dir)
    release_evidence = _load_json_object(
        artifact_dir / ARTIFACT_MANIFEST_DIRNAME / "release_evidence.json"
    )
    if release_evidence is None:
        raise FileNotFoundError("release evidence is required to build the intelligence bundle")
    bundle = build_archive_intelligence_bundle(release_evidence, root=root)
    output_dir.mkdir(parents=True, exist_ok=True)
    write_json(output_dir / "archive_maturity.json", bundle["maturity"])
    write_json(output_dir / "source_observability.json", bundle["source_observability"])
    write_json(output_dir / "privacy_rights_score.json", bundle["privacy_rights_scoring"])
    write_json(output_dir / "anomaly_report.json", bundle["anomaly_report"])
    write_json(output_dir / "public_claims.json", bundle["public_claims"])
    write_json(output_dir / "federation_compatibility.json", bundle["federation_compatibility"])
    for filename, text in bundle["public_claims"]["markdown"].items():
        (output_dir / f"{Path(filename).stem}.claims.md").write_text(str(text), encoding="utf-8")
    write_json(
        output_dir / "archive_intelligence_manifest.json",
        {
            "schema_version": ARCHIVE_INTELLIGENCE_SCHEMA_VERSION,
            "generated_at": utc_now_iso(),
            "files": sorted(
                [
                    "archive_maturity.json",
                    "source_observability.json",
                    "privacy_rights_score.json",
                    "anomaly_report.json",
                    "public_claims.json",
                    "federation_compatibility.json",
                    "README.claims.md",
                    "dataset-card.claims.md",
                    "release-notes.claims.md",
                    "github-project-summary.claims.md",
                ]
            ),
        },
    )
    return bundle


def validate_archive_intelligence_report(
    report: Mapping[str, Any],
    *,
    strict: bool = False,
    minimum_score: int = 100,
) -> list[str]:
    """Validate maturity report thresholds for publication gating."""
    failures: list[str] = []
    score = float(report.get("score", 0))
    severity = str(report.get("severity", ""))
    if strict and score < minimum_score:
        failures.append(
            f"Archive maturity score {score:.2f} is below strict minimum {minimum_score}."
        )
    if strict and severity != "leading":
        failures.append(
            f"Archive maturity severity {severity!r} is not acceptable for strict mode."
        )
    return failures


def write_archive_intelligence_report(
    release_evidence_path: Path,
    output_path: Path,
) -> JsonObject:
    """Write archive maturity intelligence derived from release evidence."""
    report = build_archive_intelligence_from_file(release_evidence_path)
    write_json(output_path, report)
    return report


def write_archive_intelligence_report_from_artifact_dir(
    artifact_dir: Path,
    output_path: Path,
) -> JsonObject:
    """Write archive maturity intelligence derived from a monthly artifact directory."""
    report = build_archive_intelligence_from_artifact_dir(artifact_dir)
    write_json(output_path, report)
    return report
