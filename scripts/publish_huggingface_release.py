"""Publish monthly archive artifacts to Hugging Face and verify readback."""

from __future__ import annotations

import argparse
import json
import os
import sys
import tempfile
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from huggingface_hub import snapshot_download, upload_folder  # noqa: E402

from corpus_cases_medilegal_nz.archive import (  # noqa: E402
    derive_archive_version,
    sha256_file,
    write_json,
)


def _commit_field(commit_info: object, field: str) -> str:
    return str(getattr(commit_info, field, "") or "")


def publish_to_hugging_face(
    artifact_dir: Path,
    repo_id: str,
    token: str,
    archive_version: str,
    dry_run: bool = False,
) -> dict[str, Any]:
    """Upload a release artifact folder and verify the manifest from the hub."""
    artifact_dir = Path(artifact_dir)
    manifest_path = artifact_dir / "manifests/release_evidence.json"
    if not manifest_path.is_file():
        msg = f"release evidence manifest is missing: {manifest_path}"
        raise FileNotFoundError(msg)

    path_in_repo = f"releases/{archive_version}"
    local_manifest_sha256 = sha256_file(manifest_path)
    evidence: dict[str, Any] = {
        "schema_version": "1.0.0",
        "archive_version": archive_version,
        "repo_id": repo_id,
        "path_in_repo": path_in_repo,
        "local_manifest_sha256": local_manifest_sha256,
        "dry_run": dry_run,
        "uploaded": False,
        "remote_manifest_verified": False,
    }
    if dry_run:
        write_json(artifact_dir / "manifests/huggingface_publish_evidence.json", evidence)
        return evidence
    if not token:
        msg = "HF_TOKEN is required for Hugging Face publication."
        raise RuntimeError(msg)

    commit_info = upload_folder(
        repo_id=repo_id,
        repo_type="dataset",
        folder_path=str(artifact_dir),
        path_in_repo=path_in_repo,
        token=token,
        commit_message=f"Publish monthly archive {archive_version}",
    )
    revision = _commit_field(commit_info, "oid") or _commit_field(commit_info, "commit_id")
    commit_url = _commit_field(commit_info, "commit_url")
    with tempfile.TemporaryDirectory(prefix="medilegal-hf-verify-") as tmp:
        snapshot_dir = Path(
            snapshot_download(
                repo_id=repo_id,
                repo_type="dataset",
                revision=revision or "main",
                allow_patterns=[f"{path_in_repo}/manifests/release_evidence.json"],
                local_dir=tmp,
                token=token,
            )
        )
        remote_manifest = snapshot_dir / path_in_repo / "manifests/release_evidence.json"
        remote_manifest_sha256 = sha256_file(remote_manifest)

    evidence.update(
        {
            "uploaded": True,
            "revision": revision,
            "commit_url": commit_url,
            "remote_manifest_sha256": remote_manifest_sha256,
            "remote_manifest_verified": remote_manifest_sha256 == local_manifest_sha256,
        }
    )
    write_json(artifact_dir / "manifests/huggingface_publish_evidence.json", evidence)
    if not evidence["remote_manifest_verified"]:
        msg = "Uploaded Hugging Face manifest hash did not match local manifest hash."
        raise RuntimeError(msg)
    return evidence


def main(argv: list[str] | None = None) -> int:
    """Run the Hugging Face monthly release publisher."""
    parser = argparse.ArgumentParser(
        description="Publish monthly archive artifacts to Hugging Face."
    )
    parser.add_argument("--artifact-dir", default="generated/monthly-publication")
    parser.add_argument("--archive-version", default="")
    parser.add_argument("--repo-id", default=os.environ.get("HF_REPO_ID", ""))
    parser.add_argument("--token-env", default="HF_TOKEN")
    parser.add_argument("--dry-run", action="store_true")
    ns = parser.parse_args(argv)
    repo_id = ns.repo_id or "edithatogo/corpus-cases-medilegal-nz"
    archive_version = ns.archive_version or derive_archive_version()
    evidence = publish_to_hugging_face(
        artifact_dir=Path(ns.artifact_dir),
        repo_id=repo_id,
        token=os.environ.get(ns.token_env, ""),
        archive_version=archive_version,
        dry_run=ns.dry_run,
    )
    sys.stdout.write(json.dumps(evidence, indent=2, sort_keys=True) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
