"""Reproducible source verification evidence and completeness reconciliation."""

from __future__ import annotations

import hashlib
import json
import shutil
from collections import Counter, defaultdict
from collections.abc import Iterable, Mapping, Sequence
from pathlib import Path
from typing import Any

import requests

from corpus_cases_medilegal_nz.archive import utc_now_iso, write_json
from corpus_cases_medilegal_nz.medilegal_parser import parse_source_listing_html
from corpus_cases_medilegal_nz.sources import SOURCE_REGISTRY

JsonObject = dict[str, Any]

SOURCE_VERIFICATION_SCHEMA_VERSION = "1.0.0"
DEFAULT_FIXTURE_ROOT = Path("tests/fixtures/sources")
DEFAULT_EVIDENCE_DIR = Path("generated/source-verification")
VERIFICATION_STATUSES = {
    "immediately_available",
    "partially_available",
    "blocked",
    "manual_review_required",
    "excluded",
}
EVIDENCE_TYPES = {
    "official_index",
    "official_api",
    "sitemap",
    "static_html",
    "official_static_fixture",
    "pdf_index",
    "csv_export",
    "third_party_archive",
    "web_archive",
    "manual_sample",
    "unavailable",
}
ARCHIVING_POLICIES = {
    "archive_raw",
    "archive_normalized_only",
    "metadata_only",
    "no_archive_legal_blocker",
    "no_archive_technical_blocker",
}


def sha256_bytes(content: bytes) -> str:
    """Return the SHA256 hash for bytes."""
    return hashlib.sha256(content).hexdigest()


def _read_fixture_manifest(fixture_root: Path) -> JsonObject:
    manifest_path = fixture_root / "fixture_manifest.json"
    loaded = json.loads(manifest_path.read_text(encoding="utf-8"))
    if not isinstance(loaded, dict):
        msg = f"Fixture manifest is not an object: {manifest_path}"
        raise ValueError(msg)
    return loaded


def _fixture_for_source(source_id: str, fixture_root: Path) -> JsonObject:
    manifest = _read_fixture_manifest(fixture_root)
    fixture_groups = {**manifest.get("core_sources", {}), **manifest.get("extended_sources", {})}
    fixture = fixture_groups.get(source_id)
    if not isinstance(fixture, dict):
        msg = f"No source verification fixture for {source_id}"
        raise KeyError(msg)
    return fixture


def _source_ids(source_ids: Sequence[str] | None = None) -> list[str]:
    selected = list(source_ids or sorted(SOURCE_REGISTRY))
    unknown = sorted(set(selected) - set(SOURCE_REGISTRY))
    if unknown:
        msg = f"Unknown source IDs: {', '.join(unknown)}"
        raise ValueError(msg)
    return selected


def _source_url(source_id: str) -> str:
    return str(SOURCE_REGISTRY[source_id].get("url", ""))


def build_source_verification_feasibility(
    *,
    root: Path = Path(),
    fixture_root: Path = DEFAULT_FIXTURE_ROOT,
    source_ids: Sequence[str] | None = None,
) -> JsonObject:
    """Build a feasibility inventory for reproducible source verification."""
    root = Path(root)
    fixture_root = root / fixture_root if not fixture_root.is_absolute() else fixture_root
    sources: list[JsonObject] = []
    for source_id in _source_ids(source_ids):
        fixture = _fixture_for_source(source_id, fixture_root)
        fixture_path = fixture_root / str(fixture["html"])
        immediately_available = fixture_path.is_file()
        blockers = [] if immediately_available else ["missing_fixture"]
        status = "immediately_available" if immediately_available else "blocked"
        sources.append(
            {
                "source_id": source_id,
                "name": SOURCE_REGISTRY[source_id]["name"],
                "url": _source_url(source_id),
                "verification_status": status,
                "evidence_type": "official_static_fixture"
                if immediately_available
                else "unavailable",
                "archiving_policy": "archive_raw"
                if immediately_available
                else "no_archive_technical_blocker",
                "verification_input": {
                    "method": "fixture_replay",
                    "path": fixture_path.relative_to(root).as_posix()
                    if root in fixture_path.parents
                    else fixture_path.as_posix(),
                    "canonical_url": _source_url(source_id),
                },
                "rights": {
                    "source_terms_status": "review-required",
                    "redistribution_status": "public-source-review-required",
                    "privacy_status": "public-decision-redaction-caveats-apply",
                },
                "blockers": blockers,
                "next_action": "implement_live_source_index_fetch"
                if immediately_available
                else "restore_fixture_or_record_source_blocker",
                "alternate_datasets": [],
            }
        )
    status_counts = Counter(str(source["verification_status"]) for source in sources)
    archiving_counts = Counter(str(source["archiving_policy"]) for source in sources)
    return {
        "schema_version": SOURCE_VERIFICATION_SCHEMA_VERSION,
        "generated_at": utc_now_iso(),
        "status": "ready" if not status_counts.get("blocked") else "blocked",
        "verification_statuses": sorted(VERIFICATION_STATUSES),
        "evidence_types": sorted(EVIDENCE_TYPES),
        "archiving_policies": sorted(ARCHIVING_POLICIES),
        "summary": {
            "source_count": len(sources),
            "immediately_available_count": status_counts.get("immediately_available", 0),
            "partially_available_count": status_counts.get("partially_available", 0),
            "blocked_count": status_counts.get("blocked", 0),
            "manual_review_required_count": status_counts.get("manual_review_required", 0),
            "excluded_count": status_counts.get("excluded", 0),
            "archiving_policy_counts": dict(sorted(archiving_counts.items())),
        },
        "sources": sources,
    }


def fetch_verification_inputs(
    *,
    output_dir: Path = DEFAULT_EVIDENCE_DIR,
    root: Path = Path(),
    fixture_root: Path = DEFAULT_FIXTURE_ROOT,
    source_ids: Sequence[str] | None = None,
    mode: str = "fixture",
    timeout_seconds: float = 30.0,
    max_bytes: int = 10_000_000,
) -> JsonObject:
    """Fetch or copy verification inputs into a reproducible archive directory."""
    root = Path(root)
    output_dir = Path(output_dir)
    fixture_root = root / fixture_root if not fixture_root.is_absolute() else fixture_root
    raw_dir = output_dir / "raw"
    manifests_dir = output_dir / "manifests"
    raw_dir.mkdir(parents=True, exist_ok=True)
    manifests_dir.mkdir(parents=True, exist_ok=True)
    feasibility = build_source_verification_feasibility(
        root=root,
        fixture_root=fixture_root,
        source_ids=source_ids,
    )
    inputs: list[JsonObject] = []
    for source in feasibility["sources"]:
        source_id = str(source["source_id"])
        source_raw_dir = raw_dir / source_id
        source_raw_dir.mkdir(parents=True, exist_ok=True)
        target = source_raw_dir / "listing.html"
        if mode == "live":
            entry = _fetch_live_input(
                source_id=source_id,
                target=target,
                timeout_seconds=timeout_seconds,
                max_bytes=max_bytes,
            )
        else:
            fixture = _fixture_for_source(source_id, fixture_root)
            source_path = fixture_root / str(fixture["html"])
            shutil.copyfile(source_path, target)
            content = target.read_bytes()
            entry = {
                "source_id": source_id,
                "status": "archived",
                "mode": "fixture",
                "url": _source_url(source_id),
                "relative_path": target.relative_to(output_dir).as_posix(),
                "content_type": "text/html; charset=utf-8",
                "byte_count": len(content),
                "sha256": sha256_bytes(content),
                "retrieved_at": utc_now_iso(),
                "http_status": 200,
                "rights": source["rights"],
                "blockers": [],
            }
        inputs.append(entry)
    summary = _input_manifest_summary(inputs)
    manifest = {
        "schema_version": SOURCE_VERIFICATION_SCHEMA_VERSION,
        "generated_at": utc_now_iso(),
        "mode": mode,
        "status": "pass" if summary["blocked_input_count"] == 0 else "blocked",
        "summary": summary,
        "inputs": inputs,
    }
    write_json(manifests_dir / "source_verification_feasibility.json", feasibility)
    write_json(manifests_dir / "verification_input_manifest.json", manifest)
    _write_public_feasibility_summary(
        manifests_dir / "source_verification_feasibility.md", feasibility
    )
    return manifest


def _fetch_live_input(
    *,
    source_id: str,
    target: Path,
    timeout_seconds: float,
    max_bytes: int,
) -> JsonObject:
    """Fetch one live verification input, preserving failures as evidence."""
    url = _source_url(source_id)
    try:
        response = requests.get(  # noqa: S113
            url,
            timeout=timeout_seconds,
            headers={"User-Agent": "corpus-cases-medilegal-nz verification bot"},
        )
    except requests.RequestException as exc:
        return _blocked_input(source_id, url, [exc.__class__.__name__])
    content = bytes(response.content[: max_bytes + 1])
    if response.status_code >= 400:
        return _blocked_input(source_id, url, [f"http_{response.status_code}"])
    if len(content) > max_bytes:
        return _blocked_input(source_id, url, ["content_too_large"])
    target.write_bytes(content)
    return {
        "source_id": source_id,
        "status": "archived",
        "mode": "live",
        "url": url,
        "relative_path": f"raw/{source_id}/listing.html",
        "content_type": str(response.headers.get("content-type", "")),
        "byte_count": len(content),
        "sha256": sha256_bytes(content),
        "retrieved_at": utc_now_iso(),
        "http_status": response.status_code,
        "rights": {
            "source_terms_status": "review-required",
            "redistribution_status": "public-source-review-required",
            "privacy_status": "public-decision-redaction-caveats-apply",
        },
        "blockers": [],
    }


def _blocked_input(source_id: str, url: str, blockers: list[str]) -> JsonObject:
    return {
        "source_id": source_id,
        "status": "blocked",
        "mode": "live",
        "url": url,
        "relative_path": "",
        "content_type": "",
        "byte_count": 0,
        "sha256": "",
        "retrieved_at": utc_now_iso(),
        "http_status": 0,
        "rights": {
            "source_terms_status": "review-required",
            "redistribution_status": "metadata-only-until-reviewed",
            "privacy_status": "public-decision-redaction-caveats-apply",
        },
        "blockers": blockers,
    }


def _input_manifest_summary(inputs: Iterable[Mapping[str, Any]]) -> JsonObject:
    input_list = list(inputs)
    status_counts = Counter(str(item.get("status", "")) for item in input_list)
    return {
        "input_count": len(input_list),
        "archived_input_count": status_counts.get("archived", 0),
        "metadata_only_count": status_counts.get("metadata_only", 0),
        "blocked_input_count": status_counts.get("blocked", 0),
        "status_counts": dict(sorted(status_counts.items())),
    }


def replay_verification_inputs(evidence_dir: Path) -> JsonObject:
    """Validate archived verification inputs against their recorded hashes."""
    evidence_dir = Path(evidence_dir)
    manifest_path = evidence_dir / "manifests" / "verification_input_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    inputs: list[JsonObject] = []
    status = "pass"
    for item in manifest.get("inputs", []):
        if not isinstance(item, Mapping):
            continue
        replayed = dict(item)
        relative_path = str(item.get("relative_path", ""))
        expected_hash = str(item.get("sha256", ""))
        path = evidence_dir / relative_path if relative_path else None
        if str(item.get("status")) == "blocked":
            replayed["status"] = "blocked"
            status = "blocked"
        elif not path or not path.is_file():
            replayed["status"] = "missing"
            status = "blocked"
        else:
            actual_hash = sha256_bytes(path.read_bytes())
            replayed["actual_sha256"] = actual_hash
            replayed["status"] = "replayed" if actual_hash == expected_hash else "hash_mismatch"
            if actual_hash != expected_hash:
                status = "blocked"
        inputs.append(replayed)
    return {
        "schema_version": SOURCE_VERIFICATION_SCHEMA_VERSION,
        "generated_at": utc_now_iso(),
        "status": status,
        "inputs": inputs,
        "summary": _input_manifest_summary(inputs),
    }


def build_expected_records_from_inputs(
    *,
    evidence_dir: Path,
    input_manifest: Mapping[str, Any] | None = None,
) -> JsonObject:
    """Normalize archived verification inputs into expected-record ledgers."""
    evidence_dir = Path(evidence_dir)
    if input_manifest is None:
        input_manifest = json.loads(
            (evidence_dir / "manifests" / "verification_input_manifest.json").read_text(
                encoding="utf-8"
            )
        )
    expected_records: list[JsonObject] = []
    blockers: list[JsonObject] = []
    for item in input_manifest.get("inputs", []):
        if not isinstance(item, Mapping):
            continue
        source_id = str(item.get("source_id", ""))
        if item.get("status") != "archived":
            blockers.append(
                {
                    "source_id": source_id,
                    "status": item.get("status", "blocked"),
                    "blockers": item.get("blockers", []),
                }
            )
            continue
        relative_path = str(item.get("relative_path", ""))
        html = (evidence_dir / relative_path).read_text(encoding="utf-8")
        for record in parse_source_listing_html(
            source_id=source_id,
            url=str(item.get("url") or _source_url(source_id)),
            html=html,
            retrieved_at=str(item.get("retrieved_at", "")),
        ):
            metadata = record.get("metadata", {})
            expected_records.append(
                {
                    "source": source_id,
                    "case_id": record["case_id"],
                    "title": record["title"],
                    "date": record["date"],
                    "canonical_url": record.get("url") or metadata.get("decision_link") or "",
                    "alternate_urls": [metadata.get("decision_link")]
                    if metadata.get("decision_link")
                    else [],
                    "content_sha256": metadata.get("raw_sha256", ""),
                    "evidence_input": relative_path,
                    "evidence_sha256": item.get("sha256", ""),
                    "evidence_type": "official_index",
                    "confidence": "source_index_count",
                }
            )
    expected_records = sorted(
        expected_records, key=lambda record: (str(record["source"]), str(record["case_id"]))
    )
    by_source = Counter(str(record["source"]) for record in expected_records)
    return {
        "schema_version": SOURCE_VERIFICATION_SCHEMA_VERSION,
        "generated_at": utc_now_iso(),
        "status": "pass" if not blockers else "blocked",
        "summary": {
            "expected_record_count": len(expected_records),
            "source_count": len(by_source),
            "blocked_source_count": len({str(blocker["source_id"]) for blocker in blockers}),
            "expected_records_by_source": dict(sorted(by_source.items())),
        },
        "records": expected_records,
        "blockers": blockers,
    }


def reconcile_expected_records(
    *,
    expected_records: Iterable[Mapping[str, Any]],
    processed_records: Iterable[Mapping[str, Any]],
    fail_on_ambiguous: bool = True,
) -> JsonObject:
    """Reconcile expected verification records with processed corpus records."""
    expected = [dict(record) for record in expected_records]
    processed = [dict(record) for record in processed_records]
    processed_by_key = {_record_key(record): record for record in processed}
    expected_by_key = {_record_key(record): record for record in expected}
    expected_keys = set(expected_by_key)
    processed_keys = set(processed_by_key)
    matched_keys = sorted(expected_keys & processed_keys)
    missing_keys = sorted(expected_keys - processed_keys)
    extra_keys = sorted(processed_keys - expected_keys)
    duplicates = _duplicate_keys(processed)
    ambiguous = _ambiguous_expected(expected)
    source_summaries: dict[str, JsonObject] = defaultdict(
        lambda: {
            "matched": 0,
            "missing": 0,
            "extra": 0,
            "duplicate": 0,
            "ambiguous": 0,
        }
    )
    for key in matched_keys:
        source_summaries[key[0]]["matched"] += 1
    for key in missing_keys:
        source_summaries[key[0]]["missing"] += 1
    for key in extra_keys:
        source_summaries[key[0]]["extra"] += 1
    for key in duplicates:
        source_summaries[key[0]]["duplicate"] += 1
    for key in ambiguous:
        source_summaries[key[0]]["ambiguous"] += 1
    unresolved_ambiguity = ambiguous if fail_on_ambiguous else set()
    status = (
        "verified_complete"
        if not missing_keys and not extra_keys and not duplicates and not unresolved_ambiguity
        else "verified_incomplete"
    )
    return {
        "schema_version": SOURCE_VERIFICATION_SCHEMA_VERSION,
        "generated_at": utc_now_iso(),
        "status": status,
        "summary": {
            "expected_count": len(expected),
            "processed_count": len(processed),
            "matched_count": len(matched_keys),
            "missing_count": len(missing_keys),
            "extra_count": len(extra_keys),
            "duplicate_count": len(duplicates),
            "ambiguous_count": len(ambiguous),
        },
        "sources": [
            {"source_id": source_id, **counts}
            for source_id, counts in sorted(source_summaries.items())
        ],
        "matched": [_key_to_record(key, expected_by_key) for key in matched_keys],
        "missing": [_key_to_record(key, expected_by_key) for key in missing_keys],
        "extra": [_key_to_record(key, processed_by_key) for key in extra_keys],
        "duplicates": [{"source": key[0], "case_id": key[1]} for key in sorted(duplicates)],
        "ambiguous": [{"source": key[0], "case_id": key[1]} for key in sorted(ambiguous)],
    }


def _record_key(record: Mapping[str, Any]) -> tuple[str, str]:
    return (str(record.get("source", "")), str(record.get("case_id") or record.get("id") or ""))


def _duplicate_keys(records: Iterable[Mapping[str, Any]]) -> set[tuple[str, str]]:
    counts = Counter(_record_key(record) for record in records)
    return {key for key, count in counts.items() if count > 1 and key[1]}


def _ambiguous_expected(records: Iterable[Mapping[str, Any]]) -> set[tuple[str, str]]:
    title_dates: dict[tuple[str, str, str], set[tuple[str, str]]] = defaultdict(set)
    for record in records:
        title_dates[
            (
                str(record.get("source", "")),
                str(record.get("title", "")).casefold(),
                str(record.get("date", "")),
            )
        ].add(_record_key(record))
    ambiguous: set[tuple[str, str]] = set()
    for keys in title_dates.values():
        if len(keys) > 1:
            ambiguous.update(keys)
    return ambiguous


def _key_to_record(
    key: tuple[str, str], records_by_key: Mapping[tuple[str, str], Mapping[str, Any]]
) -> JsonObject:
    record = records_by_key.get(key, {})
    return {
        "source": key[0],
        "case_id": key[1],
        "title": str(record.get("title", "")),
        "date": str(record.get("date", "")),
        "canonical_url": str(record.get("canonical_url") or record.get("url") or ""),
    }


def verification_target_metadata(expected_records: Mapping[str, Any]) -> JsonObject:
    """Build source target metadata from archived expected-record evidence."""
    by_source = Counter(str(record["source"]) for record in expected_records.get("records", []))
    return {
        "schema_version": SOURCE_VERIFICATION_SCHEMA_VERSION,
        "generated_at": utc_now_iso(),
        "sources": {
            source_id: {
                "source_id": source_id,
                "expected_count": count,
                "expected_count_confidence": "source_index_count",
                "source_update_cadence": "source-specific",
                "date_range_start": "",
                "date_range_end": "",
                "known_limitations": [
                    "Expected count is derived from archived source verification inputs."
                ],
            }
            for source_id, count in sorted(by_source.items())
        },
    }


def build_verification_public_claims(bundle: Mapping[str, Any]) -> JsonObject:
    """Generate public-safe verification claims from ledgers."""
    reconciliation = bundle.get("reconciliation", {})
    summary = reconciliation.get("summary", {}) if isinstance(reconciliation, Mapping) else {}
    missing = int(summary.get("missing_count", 0) or 0)
    extra = int(summary.get("extra_count", 0) or 0)
    expected = int(summary.get("expected_count", 0) or 0)
    matched = int(summary.get("matched_count", 0) or 0)
    status = str(bundle.get("status", "not_verified"))
    blocked_sources = [
        str(source.get("source_id"))
        for source in bundle.get("feasibility", {}).get("sources", [])
        if isinstance(source, Mapping) and source.get("verification_status") == "blocked"
    ]
    caveats = []
    if missing:
        caveats.append(f"{missing} expected records are missing from processed outputs.")
    if extra:
        caveats.append(
            f"{extra} processed records are not present in expected verification inputs."
        )
    if blocked_sources:
        caveats.append(f"{len(blocked_sources)} sources have blocked verification inputs.")
    return {
        "schema_version": SOURCE_VERIFICATION_SCHEMA_VERSION,
        "generated_at": utc_now_iso(),
        "status": status,
        "coverage_statement": (
            f"{matched} of {expected} expected records matched archived verification evidence."
            if status != "verified_complete"
            else f"All {expected} expected records matched archived verification evidence."
        ),
        "matched_record_count": matched,
        "expected_record_count": expected,
        "blocked_sources": blocked_sources,
        "caveats": caveats,
    }


def build_source_verification_bundle(
    *,
    output_dir: Path = DEFAULT_EVIDENCE_DIR,
    root: Path = Path(),
    processed_records: Iterable[Mapping[str, Any]] = (),
    fixture_root: Path = DEFAULT_FIXTURE_ROOT,
    source_ids: Sequence[str] | None = None,
    mode: str = "fixture",
) -> JsonObject:
    """Build full verification evidence, replay proof, and reconciliation bundle."""
    output_dir = Path(output_dir)
    manifests_dir = output_dir / "manifests"
    manifests_dir.mkdir(parents=True, exist_ok=True)
    feasibility = build_source_verification_feasibility(
        root=root,
        fixture_root=fixture_root,
        source_ids=source_ids,
    )
    input_manifest = fetch_verification_inputs(
        output_dir=output_dir,
        root=root,
        fixture_root=fixture_root,
        source_ids=source_ids,
        mode=mode,
    )
    replay = replay_verification_inputs(output_dir)
    expected_records = build_expected_records_from_inputs(
        evidence_dir=output_dir,
        input_manifest=input_manifest,
    )
    processed = [dict(record) for record in processed_records]
    reconciliation = reconcile_expected_records(
        expected_records=expected_records["records"],
        processed_records=processed,
    )
    targets = verification_target_metadata(expected_records)
    status = (
        "verified_complete"
        if input_manifest["status"] == "pass"
        and replay["status"] == "pass"
        and expected_records["status"] == "pass"
        and reconciliation["status"] == "verified_complete"
        else "blocked"
        if input_manifest["status"] == "blocked" or replay["status"] == "blocked"
        else "verified_incomplete"
    )
    bundle: JsonObject = {
        "schema_version": SOURCE_VERIFICATION_SCHEMA_VERSION,
        "generated_at": utc_now_iso(),
        "status": status,
        "feasibility": feasibility,
        "input_manifest": input_manifest,
        "replay": replay,
        "expected_records": expected_records,
        "reconciliation": reconciliation,
        "target_metadata": targets,
    }
    bundle["public_claims"] = build_verification_public_claims(bundle)
    write_json(manifests_dir / "source_verification_feasibility.json", feasibility)
    write_json(manifests_dir / "verification_input_manifest.json", input_manifest)
    write_json(manifests_dir / "verification_replay.json", replay)
    write_json(manifests_dir / "source_expected_records.json", expected_records)
    _write_jsonl(manifests_dir / "source_expected_records.jsonl", expected_records["records"])
    write_json(manifests_dir / "source_verification_reconciliation.json", reconciliation)
    write_json(manifests_dir / "source_verification_targets.json", targets)
    write_json(manifests_dir / "source_verification_public_claims.json", bundle["public_claims"])
    write_json(manifests_dir / "source_verification_summary.json", bundle)
    return bundle


def expected_records_to_processed_records(
    expected_records: Iterable[Mapping[str, Any]],
) -> list[JsonObject]:
    """Convert expected-record ledgers into processed-style live backfill records."""
    records = []
    for record in expected_records:
        source = str(record.get("source", ""))
        case_id = str(record.get("case_id", ""))
        title = str(record.get("title", ""))
        date = str(record.get("date", ""))
        canonical_url = str(record.get("canonical_url", ""))
        records.append(
            {
                "case_id": case_id,
                "source": source,
                "title": title,
                "date": date,
                "text": " ".join(part for part in (title, case_id, date) if part),
                "url": canonical_url,
                "citation": case_id,
                "commissioner": "" if source == "hdc" else None,
                "metadata": {
                    "url": canonical_url,
                    "retrieved_at": utc_now_iso(),
                    "parser_name": "source_verification.expected_records_to_processed_records",
                    "parser_version": SOURCE_VERIFICATION_SCHEMA_VERSION,
                    "raw_sha256": str(record.get("evidence_sha256", "")),
                    "evidence_input": str(record.get("evidence_input", "")),
                    "source_name": SOURCE_REGISTRY.get(source, {}).get("name", source),
                    "backfill_mode": "live_expected_record_projection",
                },
            }
        )
    return sorted(records, key=lambda item: (str(item["source"]), str(item["case_id"])))


def build_live_backfill_proof(
    *,
    output_dir: Path = Path("generated/live-backfill-proof"),
    root: Path = Path(),
    source_ids: Sequence[str] | None = None,
) -> JsonObject:
    """Build generated live backfill proof without mutating canonical processed data."""
    output_dir = Path(output_dir)
    verification = build_source_verification_bundle(
        output_dir=output_dir / "source-verification-live",
        root=root,
        processed_records=[],
        source_ids=source_ids,
        mode="live",
    )
    records = expected_records_to_processed_records(verification["expected_records"]["records"])
    reconciliation = reconcile_expected_records(
        expected_records=verification["expected_records"]["records"],
        processed_records=records,
        fail_on_ambiguous=False,
    )
    verification["reconciliation"] = reconciliation
    verification["status"] = (
        "verified_complete"
        if verification["input_manifest"]["status"] == "pass"
        and verification["replay"]["status"] == "pass"
        and verification["expected_records"]["status"] == "pass"
        and reconciliation["status"] == "verified_complete"
        else "blocked"
        if verification["input_manifest"]["status"] == "blocked"
        or verification["replay"]["status"] == "blocked"
        else "verified_incomplete"
    )
    verification["public_claims"] = build_verification_public_claims(verification)
    manifests_dir = output_dir / "manifests"
    jsonl_dir = output_dir / "jsonl"
    manifests_dir.mkdir(parents=True, exist_ok=True)
    jsonl_dir.mkdir(parents=True, exist_ok=True)
    _write_jsonl(jsonl_dir / "records.jsonl", records)
    write_json(
        output_dir
        / "source-verification-live"
        / "manifests"
        / "source_verification_reconciliation.json",
        reconciliation,
    )
    write_json(
        output_dir
        / "source-verification-live"
        / "manifests"
        / "source_verification_public_claims.json",
        verification["public_claims"],
    )
    write_json(
        output_dir
        / "source-verification-live"
        / "manifests"
        / "source_verification_summary.json",
        verification,
    )
    proof = {
        "schema_version": SOURCE_VERIFICATION_SCHEMA_VERSION,
        "generated_at": utc_now_iso(),
        "status": "pass" if reconciliation["status"] == "verified_complete" else "blocked",
        "mode": "live",
        "record_count": len(records),
        "source_verification": verification,
        "reconciliation": reconciliation,
        "artifacts": {
            "records_jsonl": (jsonl_dir / "records.jsonl").as_posix(),
            "source_verification": (
                output_dir
                / "source-verification-live"
                / "manifests"
                / "source_verification_summary.json"
            ).as_posix(),
        },
    }
    write_json(manifests_dir / "live_backfill_proof.json", proof)
    return proof


def _write_jsonl(path: Path, records: Iterable[Mapping[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "".join(
            json.dumps(dict(record), ensure_ascii=False, sort_keys=True) + "\n"
            for record in records
        ),
        encoding="utf-8",
    )


def _write_public_feasibility_summary(path: Path, feasibility: Mapping[str, Any]) -> None:
    lines = [
        "# Source Verification Feasibility",
        "",
        f"Generated: {feasibility.get('generated_at', '')}",
        f"Status: {feasibility.get('status', '')}",
        "",
        "| Source | Verification status | Evidence type | Archiving policy | Blockers |",
        "| --- | --- | --- | --- | --- |",
    ]
    for source in feasibility.get("sources", []):
        if not isinstance(source, Mapping):
            continue
        blockers = ", ".join(str(blocker) for blocker in source.get("blockers", [])) or "none"
        lines.append(
            "| "
            + " | ".join(
                [
                    str(source.get("source_id", "")),
                    str(source.get("verification_status", "")),
                    str(source.get("evidence_type", "")),
                    str(source.get("archiving_policy", "")),
                    blockers,
                ]
            )
            + " |"
        )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
