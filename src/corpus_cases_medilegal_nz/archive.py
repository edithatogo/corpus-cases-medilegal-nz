"""Release, archive, and publication evidence helpers."""

from __future__ import annotations

import gzip
import hashlib
import json
import os
import re
import shutil
import tarfile
import tomllib
from collections import Counter
from collections.abc import Iterable, Mapping
from datetime import UTC, date, datetime
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from corpus_cases_medilegal_nz.config_models import (
    HdcPipelineConfig,
    PipelineConfig,
    SourceConfig,
)
from corpus_cases_medilegal_nz.parser_contract import build_parser_contract
from corpus_cases_medilegal_nz.sources import SOURCE_REGISTRY

DEFAULT_HF_REPO_ID = "edithatogo/corpus-cases-medilegal-nz"
DEFAULT_ZENODO_ENVIRONMENT = "zenodo-production"
DEFAULT_GITHUB_REPO = "edithatogo/corpus-cases-medilegal-nz"
ATTESTATION_PROVIDER = "github-artifact-attestations"
ATTESTATION_ACTION = "actions/attest-build-provenance@43d14bc2b83dec42d39ecae14e916627a18bb661"
RELEASE_EVIDENCE_SCHEMA_VERSION = "1.0.0"
SCHEMA_VERSION = "1.0.0"

JsonObject = dict[str, Any]


def utc_now_iso() -> str:
    """Return a stable UTC timestamp string."""
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def derive_archive_version(as_of: date | None = None) -> str:
    """Return the monthly dataset/archive version for a date."""
    value = as_of or datetime.now(UTC).date()
    return f"{value.year}.{value.month:02d}.0"


def release_tag(archive_version: str) -> str:
    """Return the GitHub dataset release tag for an archive version."""
    return f"dataset-v{archive_version}"


def release_asset_names(archive_version: str) -> list[str]:
    """Return GitHub release asset names expected for an archive version."""
    return [
        f"corpus-cases-medilegal-nz-{archive_version}.tar.gz",
        "SHA256SUMS",
        "release_evidence.json",
        "checksum_manifest.json",
        "source_coverage.json",
        "public_surface_audit.json",
        "metadata_packages_manifest.json",
        "sbom.cyclonedx.json",
        "sbom.spdx.json",
    ]


def sha256_file(path: Path) -> str:
    """Return the SHA-256 hex digest for a file."""
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def canonical_json(payload: Mapping[str, Any]) -> str:
    """Serialize JSON in a deterministic form for hashing and manifests."""
    return json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def write_json(path: Path, payload: Mapping[str, Any]) -> Path:
    """Write deterministic JSON and return the written path."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(canonical_json(payload), encoding="utf-8")
    return path


def iter_files(root: Path) -> Iterable[Path]:
    """Yield files below a directory in deterministic order."""
    if not root.exists():
        return []
    return sorted(path for path in root.rglob("*") if path.is_file())


def build_checksum_manifest(root: Path) -> JsonObject:
    """Build a SHA-256 checksum manifest for a directory."""
    root = Path(root)
    files: list[JsonObject] = []
    for path in iter_files(root):
        relative = path.relative_to(root).as_posix()
        files.append(
            {
                "path": relative,
                "bytes": path.stat().st_size,
                "sha256": sha256_file(path),
            }
        )
    manifest: JsonObject = {
        "schema_version": "1.0.0",
        "generated_at": utc_now_iso(),
        "root": str(root),
        "files": files,
        "file_count": len(files),
    }
    manifest["manifest_sha256"] = hashlib.sha256(
        canonical_json({"files": files}).encode("utf-8")
    ).hexdigest()
    return manifest


def write_sha256sums(root: Path, output_path: Path) -> Path:
    """Write a GNU-style SHA256SUMS file for a directory."""
    lines = []
    for path in iter_files(root):
        if path.resolve() == output_path.resolve():
            continue
        lines.append(f"{sha256_file(path)}  {path.relative_to(root).as_posix()}")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(lines) + ("\n" if lines else ""), encoding="utf-8")
    return output_path


def _record_id(record: Mapping[str, Any]) -> str:
    return str(record.get("case_id") or record.get("id") or record.get("url") or "")


def load_jsonl_records(path: Path) -> list[JsonObject]:
    """Load JSONL records from a file, returning an empty list when absent."""
    if not path.is_file():
        return []
    records: list[JsonObject] = []
    for line in path.read_text(encoding="utf-8-sig").splitlines():
        if line.strip():
            loaded = json.loads(line)
            if isinstance(loaded, dict):
                records.append(loaded)
    return records


def build_dataset_diff(
    current_records: Iterable[Mapping[str, Any]],
    previous_records: Iterable[Mapping[str, Any]] | None = None,
) -> JsonObject:
    """Build a lightweight release changelog from current and previous records."""
    current_by_id = {
        _record_id(record): dict(record) for record in current_records if _record_id(record)
    }
    previous_by_id = {
        _record_id(record): dict(record) for record in previous_records or [] if _record_id(record)
    }
    current_ids = set(current_by_id)
    previous_ids = set(previous_by_id)
    added = sorted(current_ids - previous_ids)
    removed = sorted(previous_ids - current_ids)
    changed = sorted(
        record_id
        for record_id in current_ids & previous_ids
        if current_by_id[record_id] != previous_by_id[record_id]
    )
    return {
        "schema_version": "1.0.0",
        "generated_at": utc_now_iso(),
        "added": added,
        "changed": changed,
        "removed": removed,
        "tombstoned": removed,
        "source_reconciled": sorted(current_ids),
        "counts": {
            "added": len(added),
            "changed": len(changed),
            "removed": len(removed),
            "tombstoned": len(removed),
            "current": len(current_ids),
            "previous": len(previous_ids),
        },
    }


def export_json_schemas(output_dir: Path) -> JsonObject:
    """Export Pydantic JSON schemas used by release artifacts."""
    schemas = {
        "pipeline_config": PipelineConfig.model_json_schema(),
        "hdc_pipeline_config": HdcPipelineConfig.model_json_schema(),
        "source_config": SourceConfig.model_json_schema(),
    }
    written: list[JsonObject] = []
    for name, payload in schemas.items():
        path = output_dir / f"{name}.schema.json"
        write_json(path, payload)
        written.append(
            {
                "name": name,
                "path": path.as_posix(),
                "sha256": sha256_file(path),
            }
        )
    return {
        "schema_version": SCHEMA_VERSION,
        "generated_at": utc_now_iso(),
        "schemas": written,
    }


def classify_source(source_id: str, source_info: Mapping[str, Any], root: Path) -> str:
    """Classify a configured source for coverage reporting."""
    config_exists = (root / str(source_info.get("config", ""))).is_file()
    has_url = bool(str(source_info.get("url", "")).strip())
    if source_id == "hdc" and config_exists and has_url:
        return "active"
    if has_url and config_exists:
        return "configured"
    if not has_url and config_exists:
        return "stub/planned"
    return "blocked"


def build_source_coverage(
    root: Path = Path(), records: Iterable[Mapping[str, Any]] = ()
) -> JsonObject:
    """Build a source coverage ledger aligned with sibling archive patterns."""
    root = Path(root)
    record_counts = Counter(str(record.get("source", "")) for record in records)
    sources: list[JsonObject] = []
    status_counts: Counter[str] = Counter()
    for source_id, info in SOURCE_REGISTRY.items():
        status = classify_source(source_id, info, root)
        status_counts[status] += 1
        sources.append(
            {
                "source_id": source_id,
                "name": info["name"],
                "url": info.get("url", ""),
                "config": info.get("config", ""),
                "config_exists": (root / str(info.get("config", ""))).is_file(),
                "status": status,
                "record_count": record_counts[source_id],
                "rights_status": "public-source-review-required",
                "known_exclusions": [],
            }
        )
    return {
        "schema_version": "1.0.0",
        "generated_at": utc_now_iso(),
        "classification": {
            "active": "Currently published corpus source.",
            "configured": "Config and public URL exist, but publication coverage is not yet proven.",
            "stub/planned": "Config placeholder exists; source needs URL/reconciliation work.",
            "blocked": "Source cannot be included until configuration or rights blockers are resolved.",
        },
        "status_counts": dict(sorted(status_counts.items())),
        "sources": sources,
    }


CORE_SOURCE_IDS = {"hdc", "hpdt", "moj_tribunals", "era", "teachers"}


def _source_module_exists(source_id: str, root: Path) -> bool:
    return (root / "src" / "corpus_cases_medilegal_nz" / "sources" / f"{source_id}.py").is_file()


def _source_completion_stage(
    *,
    source_id: str,
    config_exists: bool,
    has_url: bool,
    adapter_exists: bool,
    record_count: int,
) -> tuple[str, str]:
    if record_count > 0:
        return "validated_records", "published-ready local records exist for this source."
    if adapter_exists and source_id in CORE_SOURCE_IDS and has_url and config_exists:
        return "fetch_scaffold_parser_stub", (
            "source has configuration and fetch scaffolding, but no parsed local records."
        )
    if has_url and config_exists:
        return "configured_no_adapter", (
            "source has configuration and a public URL but no source-specific adapter module."
        )
    if config_exists:
        return "planned", "source has a placeholder configuration but no public URL."
    return "blocked", "source is missing required local configuration."


def build_source_collection_audit(
    root: Path = Path(), records: Iterable[Mapping[str, Any]] = ()
) -> JsonObject:
    """Build source-level collection and parser completion evidence."""
    root = Path(root)
    record_counts = Counter(str(record.get("source", "")) for record in records)
    sources: list[JsonObject] = []
    stage_counts: Counter[str] = Counter()
    for source_id, info in SOURCE_REGISTRY.items():
        config_path = root / str(info.get("config", ""))
        config_exists = config_path.is_file()
        has_url = bool(str(info.get("url", "")).strip())
        adapter_exists = _source_module_exists(source_id, root)
        record_count = record_counts[source_id]
        stage, stage_reason = _source_completion_stage(
            source_id=source_id,
            config_exists=config_exists,
            has_url=has_url,
            adapter_exists=adapter_exists,
            record_count=record_count,
        )
        stage_counts[stage] += 1
        sources.append(
            {
                "source_id": source_id,
                "name": info["name"],
                "completion_stage": stage,
                "stage_reason": stage_reason,
                "config_exists": config_exists,
                "has_public_url": has_url,
                "adapter_module_exists": adapter_exists,
                "record_count": record_count,
                "parser_contract": {
                    "shared_library": "nlp-policy-nz",
                    "contract_version": build_parser_contract()["schema_version"],
                    "status": "required" if stage != "validated_records" else "satisfied",
                    "expected_output": "list[dict] compatible with ExportableCase and release evidence records",
                },
                "next_action": _next_source_action(stage),
            }
        )
    return {
        "schema_version": "1.0.0",
        "generated_at": utc_now_iso(),
        "stage_counts": dict(sorted(stage_counts.items())),
        "completion_ladder": [
            "planned",
            "configured_no_adapter",
            "fetch_scaffold_parser_stub",
            "validated_records",
            "blocked",
        ],
        "sources": sources,
    }


def build_collection_quality_gates(
    records: Iterable[Mapping[str, Any]],
    previous_records: Iterable[Mapping[str, Any]] | None = None,
    *,
    parser_complete_sources: Iterable[str] = CORE_SOURCE_IDS,
    drift_warning_ratio: float = 0.5,
) -> JsonObject:
    """Build parser-complete zero-record gates and source drift warnings."""
    current_counts = Counter(str(record.get("source", "")) for record in records)
    previous_counts = Counter(str(record.get("source", "")) for record in previous_records or [])
    parser_complete = sorted(set(parser_complete_sources))
    blockers: list[str] = []
    warnings: list[str] = []
    summaries: list[JsonObject] = []

    for source_id in parser_complete:
        current_count = current_counts[source_id]
        previous_count = previous_counts[source_id]
        source_blockers: list[str] = []
        source_warnings: list[str] = []
        if current_count == 0:
            message = f"{source_id} is parser-complete but has zero current records."
            blockers.append(message)
            source_blockers.append(message)
        if previous_count > 0:
            drop_ratio = (previous_count - current_count) / previous_count
            if drop_ratio >= drift_warning_ratio:
                message = (
                    f"{source_id} record count dropped from {previous_count} "
                    f"to {current_count} ({drop_ratio:.0%})."
                )
                warnings.append(message)
                source_warnings.append(message)
        summaries.append(
            {
                "source_id": source_id,
                "parser_complete": True,
                "record_count": current_count,
                "previous_record_count": previous_count,
                "status": "blocked" if source_blockers else "pass",
                "blockers": source_blockers,
                "warnings": source_warnings,
            }
        )

    return {
        "schema_version": "1.0.0",
        "generated_at": utc_now_iso(),
        "status": "blocked" if blockers else "pass",
        "parser_complete_sources": parser_complete,
        "drift_warning_ratio": drift_warning_ratio,
        "blockers": blockers,
        "warnings": warnings,
        "source_validation_summaries": summaries,
    }


def _next_source_action(stage: str) -> str:
    actions = {
        "validated_records": "monitor record-count drift and quality regressions.",
        "fetch_scaffold_parser_stub": "complete parser integration and fixture tests.",
        "configured_no_adapter": "add a source-specific adapter module or explicit delegation.",
        "planned": "confirm source URL, rights posture, and adapter scope.",
        "blocked": "restore required source configuration.",
    }
    return actions.get(stage, "triage source state.")


def build_quality_report(records: Iterable[Mapping[str, Any]]) -> JsonObject:
    """Build quality signals for release gating."""
    records_list = [dict(record) for record in records]
    ids = [_record_id(record) for record in records_list]
    duplicate_ids = sorted(item for item, count in Counter(ids).items() if item and count > 1)
    missing_text = sorted(
        _record_id(record) for record in records_list if not str(record.get("text", "")).strip()
    )
    invalid_dates: list[str] = []
    malformed_urls: list[str] = []
    for record in records_list:
        record_id = _record_id(record)
        value = str(record.get("date", "")).strip()
        if value:
            try:
                date.fromisoformat(value)
            except ValueError:
                invalid_dates.append(record_id)
        url = str(record.get("url") or record.get("metadata", {}).get("url", "")).strip()
        if url:
            parsed = urlparse(url)
            if parsed.scheme not in {"http", "https"} or not parsed.netloc:
                malformed_urls.append(record_id)
    warnings = []
    if not records_list:
        warnings.append("No JSONL records found in data/processed/jsonl/records.jsonl.")
    return {
        "schema_version": "1.0.0",
        "generated_at": utc_now_iso(),
        "record_count": len(records_list),
        "duplicate_ids": duplicate_ids,
        "missing_text": missing_text,
        "invalid_dates": sorted(filter(None, invalid_dates)),
        "malformed_urls": sorted(filter(None, malformed_urls)),
        "warnings": warnings,
        "blocking_issue_count": len(duplicate_ids) + len(invalid_dates) + len(malformed_urls),
    }


def build_public_surface_audit(
    archive_version: str,
    hf_repo_id: str = DEFAULT_HF_REPO_ID,
    hf_revision: str = "",
    zenodo_record_url: str = "",
    zenodo_doi: str = "",
) -> JsonObject:
    """Build the public surface audit ledger."""
    tag = release_tag(archive_version)
    return {
        "schema_version": "1.0.0",
        "generated_at": utc_now_iso(),
        "archive_version": archive_version,
        "surfaces": {
            "github": {
                "status": "planned",
                "role": "Code, documentation, Actions, and release evidence assets.",
                "release_tag": tag,
            },
            "hugging_face": {
                "status": "active" if hf_revision else "planned",
                "role": "Live mutable dataset surface.",
                "repo_id": hf_repo_id,
                "revision": hf_revision,
            },
            "zenodo": {
                "status": "draft" if zenodo_record_url or zenodo_doi else "planned",
                "role": "Immutable DOI snapshot surface after protected approval.",
                "record_url": zenodo_record_url,
                "doi": zenodo_doi,
            },
            "osf": {
                "status": "inactive",
                "role": "Optional mirror only after a dedicated activation policy.",
            },
            "future_metadata": {
                "status": "generated-local",
                "role": "Croissant, RO-Crate, Frictionless, DCAT, PROV-O, DataCite, schema.org.",
            },
        },
        "claim_boundary": (
            "Only surfaces with evidence in this ledger may be described as active publication "
            "surfaces for this archive version."
        ),
    }


def build_legal_provenance() -> JsonObject:
    """Build release legal/privacy/provenance notes."""
    return {
        "schema_version": "1.0.0",
        "generated_at": utc_now_iso(),
        "license_scope": {
            "repository_code": "MIT",
            "source_text": "Source-specific public access and redistribution review required.",
            "archive_metadata": "Project-created metadata and manifests may be released with the archive.",
        },
        "privacy": {
            "de_anonymisation_caveat": (
                "Public decisions may contain sensitive medicolegal context. Releases must not "
                "claim anonymisation beyond the source publication."
            ),
            "takedown_contact": "Use the GitHub repository issue/contact path for correction requests.",
        },
        "known_exclusions": [
            "Private credentials and local environment files.",
            "Unreviewed source artifacts without rights evidence.",
            "Experimental endpoint artifacts not promoted by a release ladder track.",
        ],
    }


def _dependency_name(requirement: str) -> str:
    return re.split(r"[<>=!~;\[]", requirement, maxsplit=1)[0].strip()


def build_sbom(root: Path = Path()) -> JsonObject:
    """Build a lightweight CycloneDX-style SBOM from project dependencies."""
    pyproject = tomllib.loads((root / "pyproject.toml").read_text(encoding="utf-8-sig"))
    dependencies = pyproject.get("project", {}).get("dependencies", [])
    components = [
        {"type": "library", "name": _dependency_name(str(dependency)), "purl": ""}
        for dependency in dependencies
    ]
    return {
        "bomFormat": "CycloneDX",
        "specVersion": "1.5",
        "serialNumber": "urn:uuid:00000000-0000-0000-0000-000000000000",
        "version": 1,
        "metadata": {
            "timestamp": utc_now_iso(),
            "component": {"type": "application", "name": "corpus-cases-medilegal-nz"},
        },
        "components": components,
    }


def build_spdx(root: Path = Path()) -> JsonObject:
    """Build a lightweight SPDX-style package list from project dependencies."""
    sbom = build_sbom(root)
    packages = [
        {
            "SPDXID": f"SPDXRef-Package-{component['name']}",
            "name": component["name"],
            "downloadLocation": "NOASSERTION",
            "filesAnalyzed": False,
            "licenseConcluded": "NOASSERTION",
            "licenseDeclared": "NOASSERTION",
        }
        for component in sbom["components"]
    ]
    return {
        "spdxVersion": "SPDX-2.3",
        "dataLicense": "CC0-1.0",
        "SPDXID": "SPDXRef-DOCUMENT",
        "name": "corpus-cases-medilegal-nz-release-tooling",
        "documentNamespace": "https://github.com/edithatogo/corpus-cases-medilegal-nz/sbom",
        "creationInfo": {
            "created": utc_now_iso(),
            "creators": ["Tool: corpus_cases_medilegal_nz.archive"],
        },
        "packages": packages,
    }


def build_release_ladder(archive_version: str) -> JsonObject:
    """Build a release ladder manifest for canonical and experimental artifacts."""
    return {
        "schema_version": "1.0.0",
        "generated_at": utc_now_iso(),
        "archive_version": archive_version,
        "levels": [
            {
                "id": "document-level",
                "status": "canonical",
                "artifacts": ["records.jsonl", "parquet", "release evidence", "metadata packages"],
            },
            {
                "id": "endpoint",
                "status": "not-promoted",
                "artifacts": ["future linked-data or standard-specific exports"],
            },
        ],
    }


def build_attestation_verification(
    archive_version: str,
    github_repo: str = DEFAULT_GITHUB_REPO,
) -> JsonObject:
    """Build the expected GitHub artifact-attestation verification contract."""
    assets = release_asset_names(archive_version)
    release = release_tag(archive_version)
    return {
        "schema_version": "1.0.0",
        "status": "expected",
        "provider": ATTESTATION_PROVIDER,
        "attestation_action": ATTESTATION_ACTION,
        "workflow": ".github/workflows/monthly_dynamic_archive_publication.yml",
        "github_repo": github_repo,
        "release_tag": release,
        "subject_paths": [
            "generated/monthly-publication/**",
            "generated/monthly-publication-bundles/**",
        ],
        "required_release_assets": assets,
        "verification_commands": [
            f"gh attestation verify {asset} --repo {github_repo}" for asset in assets
        ],
        "notes": [
            "GitHub creates attestations after workflow artifact generation.",
            "Release readiness requires this contract before publication; live verification runs after assets exist.",
        ],
    }


def build_zenodo_metadata(
    archive_version: str,
    creators_json: str | None = None,
    hf_repo_id: str = DEFAULT_HF_REPO_ID,
) -> JsonObject:
    """Build Zenodo-compatible metadata for a draft deposition."""
    creators: Any = json.loads(creators_json) if creators_json else [{"name": "Maintainer"}]
    return {
        "metadata": {
            "title": f"New Zealand Medical-Legal Corpus {archive_version}",
            "upload_type": "dataset",
            "version": archive_version,
            "creators": creators,
            "description": (
                "Monthly version-locked snapshot of the New Zealand medical-legal corpus. "
                "The live mutable dataset is maintained on Hugging Face Datasets. "
                "Coverage is source-specific and must be interpreted with the included "
                "source coverage and release evidence ledgers."
            ),
            "license": "other-open",
            "keywords": [
                "New Zealand",
                "legal corpus",
                "medical legal",
                "Hugging Face",
                "Zenodo",
            ],
            "related_identifiers": [
                {
                    "identifier": f"https://huggingface.co/datasets/{hf_repo_id}",
                    "relation": "isSupplementedBy",
                    "scheme": "url",
                },
                {
                    "identifier": "https://github.com/edithatogo/corpus-cases-medilegal-nz",
                    "relation": "isSupplementedBy",
                    "scheme": "url",
                },
            ],
        }
    }


def build_release_evidence(
    root: Path = Path(),
    archive_version: str | None = None,
    hf_repo_id: str = DEFAULT_HF_REPO_ID,
    hf_revision: str = "",
    zenodo_draft_id: str = "",
    zenodo_record_url: str = "",
    zenodo_doi: str = "",
    zenodo_concept_doi: str = "",
    github_release_url: str = "",
    workflow_run_id: str = "",
    commit_sha: str = "",
) -> JsonObject:
    """Build a release evidence payload without writing files."""
    root = Path(root)
    version = archive_version or derive_archive_version()
    records = load_jsonl_records(root / "data/processed/jsonl/records.jsonl")
    quality = build_quality_report(records)
    coverage = build_source_coverage(root=root, records=records)
    collection_audit = build_source_collection_audit(root=root, records=records)
    dataset_diff = build_dataset_diff(records)
    collection_quality_gates = build_collection_quality_gates(records)
    public_surface = build_public_surface_audit(
        archive_version=version,
        hf_repo_id=hf_repo_id,
        hf_revision=hf_revision,
        zenodo_record_url=zenodo_record_url,
        zenodo_doi=zenodo_doi,
    )
    return {
        "schema_version": RELEASE_EVIDENCE_SCHEMA_VERSION,
        "generated_at": utc_now_iso(),
        "release": {
            "archive_version": version,
            "github_release_tag": release_tag(version),
            "github_release_url": github_release_url,
            "record_count": quality["record_count"],
            "coverage_statement": (
                "Monthly medilegal corpus archive. Current publication coverage is "
                "source-specific and evidence-backed by source_coverage.json."
            ),
        },
        "git": {
            "commit_sha": commit_sha or os.environ.get("GITHUB_SHA", ""),
            "workflow_run_id": workflow_run_id or os.environ.get("GITHUB_RUN_ID", ""),
        },
        "hugging_face": {
            "repo_id": hf_repo_id,
            "revision": hf_revision,
            "remote_manifest_verified": bool(hf_revision),
        },
        "zenodo": {
            "draft_id": zenodo_draft_id,
            "record_url": zenodo_record_url,
            "doi": zenodo_doi,
            "concept_doi": zenodo_concept_doi,
            "protected_publish_environment": DEFAULT_ZENODO_ENVIRONMENT,
            "publish_handoff_only": True,
        },
        "schema": {
            "record_schema_version": SCHEMA_VERSION,
            "compatibility": "backwards-compatible-until-schema-check-fails",
        },
        "checksums": {
            "manifest_path": "manifests/checksum_manifest.json",
            "sha256sums_path": "SHA256SUMS",
            "manifest_sha256": "",
            "artifact_count": 0,
        },
        "quality": quality,
        "parser_contract": build_parser_contract(),
        "source_coverage": coverage,
        "source_collection_audit": collection_audit,
        "collection_quality_gates": collection_quality_gates,
        "dataset_diff": dataset_diff,
        "public_surface": public_surface,
        "legal_provenance": build_legal_provenance(),
        "release_ladder": build_release_ladder(version),
        "attestation_verification": build_attestation_verification(version),
    }


def write_metadata_packages(output_dir: Path, evidence: Mapping[str, Any]) -> JsonObject:
    """Write generated discovery metadata packages and their manifest."""
    metadata_dir = output_dir / "metadata"
    metadata_dir.mkdir(parents=True, exist_ok=True)
    release = evidence["release"]
    archive_version = str(release["archive_version"])
    hf_repo_id = str(evidence["hugging_face"]["repo_id"])
    dataset_name = "New Zealand Medical-Legal Corpus"
    common = {
        "name": "corpus-cases-medilegal-nz",
        "title": dataset_name,
        "version": archive_version,
        "url": f"https://huggingface.co/datasets/{hf_repo_id}",
        "identifier": release["github_release_tag"],
        "description": release["coverage_statement"],
    }
    packages: dict[str, str | JsonObject] = {
        "croissant.jsonld": {
            "@context": "https://schema.org/",
            "@type": "Dataset",
            **common,
        },
        "ro-crate-metadata.json": {
            "@context": "https://w3id.org/ro/crate/1.1/context",
            "@graph": [{"@id": "./", "@type": "Dataset", **common}],
        },
        "datapackage.json": {
            "profile": "data-package",
            **common,
            "resources": [{"name": "records", "path": "data/processed/jsonl/records.jsonl"}],
        },
        "dcat.jsonld": {
            "@context": {"dcat": "http://www.w3.org/ns/dcat#", "dct": "http://purl.org/dc/terms/"},
            "@type": "dcat:Dataset",
            "dct:title": dataset_name,
            "dct:identifier": release["github_release_tag"],
        },
        "prov-o.jsonld": {
            "@context": {"prov": "http://www.w3.org/ns/prov#"},
            "@type": "prov:Entity",
            "prov:wasGeneratedBy": "monthly_dynamic_archive_publication",
            "prov:value": archive_version,
        },
        "datacite.json": {
            "types": {"resourceTypeGeneral": "Dataset"},
            "titles": [{"title": dataset_name}],
            "version": archive_version,
            "publisher": "Zenodo",
        },
        "schema-org-dataset.jsonld": {
            "@context": "https://schema.org",
            "@type": "Dataset",
            **common,
        },
        "huggingface-dataset-card-metadata.json": {
            "license": "mit",
            "language": ["en"],
            "tags": ["legal", "medical", "new-zealand", "medicolegal"],
            "pretty_name": dataset_name,
        },
    }
    entries: list[JsonObject] = []
    for filename, payload in packages.items():
        path = metadata_dir / filename
        if isinstance(payload, str):
            path.write_text(payload, encoding="utf-8")
        else:
            write_json(path, payload)
        entries.append({"path": path.as_posix(), "sha256": sha256_file(path)})
    manifest = {
        "schema_version": "1.0.0",
        "generated_at": utc_now_iso(),
        "packages": entries,
    }
    write_json(metadata_dir / "metadata_packages_manifest.json", manifest)
    return manifest


def build_release_artifacts(
    output_dir: Path,
    root: Path = Path(),
    archive_version: str | None = None,
    hf_repo_id: str = DEFAULT_HF_REPO_ID,
    hf_revision: str = "",
    zenodo_draft_id: str = "",
    zenodo_record_url: str = "",
    zenodo_doi: str = "",
    zenodo_concept_doi: str = "",
) -> JsonObject:
    """Write local release artifacts and return a summary."""
    output_dir = Path(output_dir)
    root = Path(root)
    for child in ("manifests", "schemas", "metadata", "sbom"):
        generated_child = output_dir / child
        if generated_child.exists():
            shutil.rmtree(generated_child)
    sha256sums = output_dir / "SHA256SUMS"
    if sha256sums.exists():
        sha256sums.unlink()
    manifests_dir = output_dir / "manifests"
    schemas_dir = output_dir / "schemas"
    sbom_dir = output_dir / "sbom"
    version = archive_version or derive_archive_version()
    evidence = build_release_evidence(
        root=root,
        archive_version=version,
        hf_repo_id=hf_repo_id,
        hf_revision=hf_revision,
        zenodo_draft_id=zenodo_draft_id,
        zenodo_record_url=zenodo_record_url,
        zenodo_doi=zenodo_doi,
        zenodo_concept_doi=zenodo_concept_doi,
    )
    write_json(manifests_dir / "release_evidence.json", evidence)
    write_json(manifests_dir / "source_coverage.json", evidence["source_coverage"])
    write_json(
        manifests_dir / "source_collection_audit.json",
        evidence["source_collection_audit"],
    )
    write_json(manifests_dir / "dataset_quality.json", evidence["quality"])
    write_json(
        manifests_dir / "collection_quality_gates.json",
        evidence["collection_quality_gates"],
    )
    write_json(manifests_dir / "parser_contract.json", evidence["parser_contract"])
    write_json(manifests_dir / "dataset_diff.json", evidence["dataset_diff"])
    write_json(manifests_dir / "public_surface_audit.json", evidence["public_surface"])
    write_json(manifests_dir / "legal_provenance.json", evidence["legal_provenance"])
    write_json(manifests_dir / "release_ladder.json", evidence["release_ladder"])
    write_json(
        manifests_dir / "attestation_verification.json",
        evidence["attestation_verification"],
    )
    schema_manifest = export_json_schemas(schemas_dir)
    metadata_manifest = write_metadata_packages(output_dir, evidence)
    write_json(sbom_dir / "sbom.cyclonedx.json", build_sbom(root))
    write_json(sbom_dir / "sbom.spdx.json", build_spdx(root))
    write_json(
        manifests_dir / "zenodo-metadata.json",
        build_zenodo_metadata(
            archive_version=version,
            creators_json=os.environ.get("ARCHIVE_CREATORS_JSON"),
            hf_repo_id=hf_repo_id,
        ),
    )
    checksum_manifest = build_checksum_manifest(output_dir)
    evidence["checksums"] = {
        "manifest_path": "manifests/checksum_manifest.json",
        "sha256sums_path": "SHA256SUMS",
        "manifest_sha256": checksum_manifest["manifest_sha256"],
        "artifact_count": checksum_manifest["file_count"],
    }
    write_json(manifests_dir / "release_evidence.json", evidence)
    checksum_manifest = build_checksum_manifest(output_dir)
    write_json(manifests_dir / "checksum_manifest.json", checksum_manifest)
    write_sha256sums(output_dir, output_dir / "SHA256SUMS")
    return {
        "output_dir": output_dir.as_posix(),
        "release_evidence": (manifests_dir / "release_evidence.json").as_posix(),
        "schema_manifest": schema_manifest,
        "metadata_manifest": metadata_manifest,
        "checksum_manifest": checksum_manifest,
    }


def build_archive_bundle(source_dir: Path, archive_path: Path) -> Path:
    """Create a deterministic tar.gz archive from a directory."""
    source_dir = Path(source_dir)
    archive_path.parent.mkdir(parents=True, exist_ok=True)
    with (
        archive_path.open("wb") as raw,
        gzip.GzipFile(filename="", fileobj=raw, mode="wb", mtime=0) as gz_file,
        tarfile.open(fileobj=gz_file, mode="w") as archive,
    ):
        for path in iter_files(source_dir):
            info = archive.gettarinfo(path, arcname=path.relative_to(source_dir).as_posix())
            info.mtime = 0
            info.uid = 0
            info.gid = 0
            info.uname = ""
            info.gname = ""
            with path.open("rb") as handle:
                archive.addfile(info, handle)
    return archive_path


def validate_release_evidence(payload: Mapping[str, Any]) -> list[str]:
    """Validate the required release evidence contract."""
    failures: list[str] = []
    for key in (
        "schema_version",
        "generated_at",
        "release",
        "git",
        "hugging_face",
        "zenodo",
        "quality",
        "source_coverage",
        "public_surface",
        "checksums",
        "attestation_verification",
    ):
        if key not in payload:
            failures.append(f"Missing release evidence key: {key}")
    release = payload.get("release", {})
    if isinstance(release, Mapping):
        version = str(release.get("archive_version", ""))
        if not re.fullmatch(r"\d{4}\.\d{2}\.0", version):
            failures.append("archive_version must use YYYY.MM.0")
        if release.get("github_release_tag") != release_tag(version):
            failures.append("github_release_tag must be dataset-v<archive_version>")
        if int(release.get("record_count", -1)) < 0:
            failures.append("record_count must be non-negative")
    else:
        failures.append("release must be an object")
    zenodo = payload.get("zenodo", {})
    if isinstance(zenodo, Mapping):
        if not zenodo.get("publish_handoff_only"):
            failures.append("Zenodo production publication must be handoff-only.")
        if not zenodo.get("protected_publish_environment"):
            failures.append("Zenodo protected publish environment must be recorded.")
    else:
        failures.append("zenodo must be an object")
    checksums = payload.get("checksums", {})
    if isinstance(checksums, Mapping):
        if not checksums.get("manifest_path"):
            failures.append("checksums.manifest_path is required")
        if not checksums.get("sha256sums_path"):
            failures.append("checksums.sha256sums_path is required")
    else:
        failures.append("checksums must be an object")
    attestation = payload.get("attestation_verification", {})
    if isinstance(attestation, Mapping):
        if attestation.get("provider") != ATTESTATION_PROVIDER:
            failures.append(
                "attestation_verification.provider must be github-artifact-attestations"
            )
        if not re.fullmatch(
            r"actions/attest-build-provenance@[0-9a-f]{40}",
            str(attestation.get("attestation_action", "")),
        ):
            failures.append("attestation_verification.attestation_action must be pinned")
        if attestation.get("status") not in {"expected", "verified"}:
            failures.append("attestation_verification.status must be expected or verified")
        for field in ("subject_paths", "required_release_assets", "verification_commands"):
            values = attestation.get(field)
            if not isinstance(values, list) or not values:
                failures.append(f"attestation_verification.{field} must be a non-empty list")
    else:
        failures.append("attestation_verification must be an object")
    return failures


def publication_readiness(
    environment: Mapping[str, str] | None = None,
    root: Path = Path(),
) -> JsonObject:
    """Check local and credential readiness for publication workflows."""
    env = environment or os.environ
    root = Path(root)
    local_required = [
        ".github/workflows/code_quality.yml",
        ".github/workflows/codeql.yml",
        ".github/workflows/monthly_dynamic_archive_publication.yml",
        ".github/workflows/osv_scan.yml",
        ".github/workflows/scorecard.yml",
        "docs/monthly-dynamic-archive-publication.md",
        "schemas/release_evidence.schema.json",
        "scripts/build_release_evidence.py",
        "scripts/check_release_evidence.py",
        "scripts/publish_huggingface_release.py",
        "scripts/publish_zenodo_draft.py",
        "uv.lock",
    ]
    checks: list[JsonObject] = []
    for relative in local_required:
        exists = (root / relative).exists()
        checks.append({"id": relative, "status": "ok" if exists else "missing"})
    credential_checks = (
        ("HF_TOKEN", ("HF_TOKEN",)),
        ("HF_REPO_ID", ("HF_REPO_ID",)),
        ("ZENODO_ACCESS_TOKEN", ("ZENODO_ACCESS_TOKEN", "ZENODO_TOKEN")),
        ("ZENODO_SANDBOX_ACCESS_TOKEN", ("ZENODO_SANDBOX_ACCESS_TOKEN", "ZENODO_SANDBOX_TOKEN")),
        ("ZENODO_API_URL", ("ZENODO_API_URL",)),
        ("ZENODO_SANDBOX_API_URL", ("ZENODO_SANDBOX_API_URL",)),
        ("ARCHIVE_CREATORS_JSON", ("ARCHIVE_CREATORS_JSON",)),
    )
    for name, aliases in credential_checks:
        configured_aliases = [alias for alias in aliases if env.get(alias)]
        checks.append(
            {
                "id": name,
                "status": "configured" if configured_aliases else "gated",
                "secret": name.endswith("TOKEN") or name == "ARCHIVE_CREATORS_JSON",
                "accepted_names": list(aliases),
                "configured_names": configured_aliases,
            }
        )
    protected_environment = env.get("ZENODO_PROTECTED_ENVIRONMENT", DEFAULT_ZENODO_ENVIRONMENT)
    environment_names = _csv_set(env.get("GITHUB_ENVIRONMENT_NAMES", ""))
    protected_environment_names = _csv_set(env.get("GITHUB_PROTECTED_ENVIRONMENT_NAMES", ""))
    if environment_names:
        environment_status = (
            "configured" if protected_environment in environment_names else "missing"
        )
    else:
        environment_status = "unknown"
    if protected_environment_names:
        protection_status = (
            "configured" if protected_environment in protected_environment_names else "missing"
        )
    else:
        protection_status = "unknown"
    checks.append(
        {
            "id": f"github_environment:{protected_environment}",
            "status": environment_status,
            "secret": False,
            "source": "GITHUB_ENVIRONMENT_NAMES",
        }
    )
    checks.append(
        {
            "id": f"github_environment_protection:{protected_environment}",
            "status": protection_status,
            "secret": False,
            "source": "GITHUB_PROTECTED_ENVIRONMENT_NAMES",
        }
    )
    blockers = [check["id"] for check in checks if check["status"] == "missing"]
    return {
        "schema_version": "1.0.0",
        "generated_at": utc_now_iso(),
        "status": "ready" if not blockers else "blocked",
        "checks": checks,
        "blockers": blockers,
        "gated_external_writes": [check["id"] for check in checks if check["status"] == "gated"],
        "protected_environment": protected_environment,
    }


def _csv_set(value: str) -> set[str]:
    """Return non-empty comma-separated values as a set."""
    return {item.strip() for item in value.split(",") if item.strip()}
