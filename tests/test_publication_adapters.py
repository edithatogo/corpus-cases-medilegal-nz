from __future__ import annotations

import json
import sys
from pathlib import Path

from corpus_cases_medilegal_nz.archive import build_archive_bundle, build_release_artifacts

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.publish_huggingface_release import publish_to_hugging_face  # noqa: E402
from scripts.publish_zenodo_draft import publish_zenodo_draft  # noqa: E402


def test_huggingface_publish_dry_run_writes_evidence(tmp_path: Path) -> None:
    artifact_dir = tmp_path / "artifact"
    build_release_artifacts(
        output_dir=artifact_dir,
        root=ROOT,
        archive_version="2026.07.0",
    )

    evidence = publish_to_hugging_face(
        artifact_dir=artifact_dir,
        repo_id="edithatogo/corpus-cases-medilegal-nz",
        token="",
        archive_version="2026.07.0",
        dry_run=True,
    )

    written = json.loads(
        (artifact_dir / "manifests/huggingface_publish_evidence.json").read_text(encoding="utf-8")
    )
    assert evidence["dry_run"] is True
    assert evidence["uploaded"] is False
    assert evidence["path_in_repo"] == "releases/2026.07.0"
    assert written["local_manifest_sha256"] == evidence["local_manifest_sha256"]


def test_zenodo_draft_dry_run_writes_handoff_evidence(tmp_path: Path) -> None:
    artifact_dir = tmp_path / "artifact"
    bundle = tmp_path / "corpus-cases-medilegal-nz-2026.07.0.tar.gz"
    build_release_artifacts(
        output_dir=artifact_dir,
        root=ROOT,
        archive_version="2026.07.0",
    )
    build_archive_bundle(artifact_dir, bundle)

    evidence = publish_zenodo_draft(
        artifact_dir=artifact_dir,
        bundle_path=bundle,
        archive_version="2026.07.0",
        token="",
        api_url="https://sandbox.zenodo.org/api",
        dry_run=True,
    )

    written = json.loads(
        (artifact_dir / "manifests/zenodo_draft_evidence.json").read_text(encoding="utf-8")
    )
    assert evidence["dry_run"] is True
    assert evidence["publish_handoff_only"] is True
    assert evidence["uploaded"] is False
    assert written["protected_publish_environment"] == "zenodo-production"
