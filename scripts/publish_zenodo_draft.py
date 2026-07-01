"""Create or update Zenodo draft releases without production publication."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any

import requests

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from corpus_cases_medilegal_nz.archive import (  # noqa: E402
    build_zenodo_metadata,
    derive_archive_version,
    sha256_file,
    write_json,
)


def _api_url(value: str) -> str:
    return value.rstrip("/") or "https://zenodo.org/api"


def _request(
    method: str,
    url: str,
    token: str,
    **kwargs: object,
) -> requests.Response:
    response = requests.request(
        method,
        url,
        params={"access_token": token},
        timeout=120,
        **kwargs,
    )
    response.raise_for_status()
    return response


def _latest_draft(token: str, response_payload: dict[str, Any]) -> dict[str, Any]:
    latest_draft = response_payload.get("links", {}).get("latest_draft")
    if latest_draft:
        return _request("GET", str(latest_draft), token).json()
    return response_payload


def _file_payloads(artifact_dir: Path, bundle_path: Path) -> list[Path]:
    files = [
        bundle_path,
        artifact_dir / "SHA256SUMS",
        artifact_dir / "manifests/release_evidence.json",
        artifact_dir / "manifests/checksum_manifest.json",
        artifact_dir / "manifests/source_coverage.json",
        artifact_dir / "manifests/public_surface_audit.json",
        artifact_dir / "metadata/metadata_packages_manifest.json",
        artifact_dir / "sbom/sbom.cyclonedx.json",
        artifact_dir / "sbom/sbom.spdx.json",
    ]
    return [path for path in files if path.is_file()]


def publish_zenodo_draft(
    artifact_dir: Path,
    bundle_path: Path,
    archive_version: str,
    token: str,
    api_url: str,
    creators_json: str = "",
    deposition_id: str = "",
    create_new_version: bool = False,
    dry_run: bool = False,
) -> dict[str, Any]:
    """Create or update a Zenodo draft deposition, but never publish it."""
    artifact_dir = Path(artifact_dir)
    bundle_path = Path(bundle_path)
    if not bundle_path.is_file():
        msg = f"Zenodo archive bundle is missing: {bundle_path}"
        raise FileNotFoundError(msg)
    files = _file_payloads(artifact_dir, bundle_path)
    if not files:
        msg = f"No Zenodo upload files found in {artifact_dir}"
        raise FileNotFoundError(msg)

    api_url = _api_url(api_url)
    metadata = build_zenodo_metadata(
        archive_version=archive_version,
        creators_json=creators_json or None,
        hf_repo_id=os.environ.get("HF_REPO_ID", "edithatogo/corpus-cases-medilegal-nz"),
    )
    evidence: dict[str, Any] = {
        "schema_version": "1.0.0",
        "archive_version": archive_version,
        "api_url": api_url,
        "deposition_id": deposition_id,
        "create_new_version": create_new_version,
        "dry_run": dry_run,
        "publish_handoff_only": True,
        "protected_publish_environment": os.environ.get(
            "ZENODO_PROTECTED_ENVIRONMENT",
            "zenodo-production",
        ),
        "files": [
            {
                "path": path.as_posix(),
                "bytes": path.stat().st_size,
                "sha256": sha256_file(path),
            }
            for path in files
        ],
        "uploaded": False,
    }
    if dry_run:
        write_json(artifact_dir / "manifests/zenodo_draft_evidence.json", evidence)
        return evidence
    if not token:
        msg = "ZENODO_ACCESS_TOKEN or ZENODO_SANDBOX_ACCESS_TOKEN is required for Zenodo draft upload."
        raise RuntimeError(msg)

    if deposition_id and create_new_version:
        response_payload = _request(
            "POST",
            f"{api_url}/deposit/depositions/{deposition_id}/actions/newversion",
            token,
        ).json()
        deposition = _latest_draft(token, response_payload)
    elif deposition_id:
        deposition = _request("GET", f"{api_url}/deposit/depositions/{deposition_id}", token).json()
    else:
        deposition = _request("POST", f"{api_url}/deposit/depositions", token, json={}).json()

    draft_id = str(deposition.get("id", deposition_id))
    _request(
        "PUT",
        f"{api_url}/deposit/depositions/{draft_id}",
        token,
        json=metadata,
    )
    bucket_url = str(deposition.get("links", {}).get("bucket", ""))
    if not bucket_url:
        msg = "Zenodo draft response did not include links.bucket."
        raise RuntimeError(msg)
    uploaded_files: list[dict[str, Any]] = []
    for path in files:
        with path.open("rb") as handle:
            upload = _request("PUT", f"{bucket_url}/{path.name}", token, data=handle)
        uploaded_files.append(
            {
                "filename": path.name,
                "status_code": upload.status_code,
                "sha256": sha256_file(path),
            }
        )

    refreshed = _request("GET", f"{api_url}/deposit/depositions/{draft_id}", token).json()
    evidence.update(
        {
            "uploaded": True,
            "deposition_id": draft_id,
            "record_url": refreshed.get("links", {}).get("html", ""),
            "doi": refreshed.get("metadata", {}).get("doi", ""),
            "concept_doi": refreshed.get("conceptdoi", ""),
            "uploaded_files": uploaded_files,
        }
    )
    write_json(artifact_dir / "manifests/zenodo_draft_evidence.json", evidence)
    return evidence


def main(argv: list[str] | None = None) -> int:
    """Run the Zenodo draft uploader."""
    parser = argparse.ArgumentParser(description="Create or update a Zenodo draft archive.")
    parser.add_argument("--artifact-dir", default="generated/monthly-publication")
    parser.add_argument("--bundle", required=True)
    parser.add_argument("--archive-version", default="")
    parser.add_argument(
        "--api-url", default=os.environ.get("ZENODO_API_URL", "https://zenodo.org/api")
    )
    parser.add_argument("--token-env", default="ZENODO_ACCESS_TOKEN")
    parser.add_argument("--deposition-id", default="")
    parser.add_argument("--create-new-version", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    ns = parser.parse_args(argv)
    evidence = publish_zenodo_draft(
        artifact_dir=Path(ns.artifact_dir),
        bundle_path=Path(ns.bundle),
        archive_version=ns.archive_version or derive_archive_version(),
        token=os.environ.get(ns.token_env, ""),
        api_url=ns.api_url,
        creators_json=os.environ.get("ARCHIVE_CREATORS_JSON", ""),
        deposition_id=ns.deposition_id,
        create_new_version=ns.create_new_version,
        dry_run=ns.dry_run,
    )
    sys.stdout.write(json.dumps(evidence, indent=2, sort_keys=True) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
