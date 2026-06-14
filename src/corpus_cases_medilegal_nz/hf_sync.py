"""Hugging Face dataset sync wrappers.

Provides download, upload, and orchestration helpers for synchronising
the local corpus with a Hugging Face dataset repository.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

from huggingface_hub import snapshot_download, upload_folder

from corpus_cases_medilegal_nz.config_models import load_pipeline_config
from corpus_cases_medilegal_nz.exporter import ExportableCase, export_all
from corpus_cases_medilegal_nz.sources import get_adapter, get_source_ids, SOURCE_REGISTRY

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Download
# ---------------------------------------------------------------------------


def download_snapshot(
    repo_id: str,
    local_dir: Path | str,
    token: str | None = None,
) -> Path:
    """Download a dataset snapshot from Hugging Face.

    Parameters
    ----------
    repo_id : str
        Hugging Face repository identifier (e.g. ``edithatogo/corpus-cases-medilegal-nz``).
    local_dir : Path or str
        Local directory to download into.
    token : str or None
        Hugging Face API token. Not required for public repos.

    Returns
    -------
    Path
        The local directory path where the snapshot was downloaded.

    Raises
    ------
    huggingface_hub.utils.HfHubHTTPError
        If the download fails due to an HTTP error.
    """
    local_path = Path(local_dir)
    local_path.mkdir(parents=True, exist_ok=True)

    logger.info("Downloading snapshot of %s to %s ...", repo_id, local_path)
    snapshot_download(
        repo_id=repo_id,
        repo_type="dataset",
        local_dir=str(local_path),
        token=token,
        resume_download=True,
    )
    logger.info("Snapshot successfully downloaded to %s", local_path)
    return local_path


# ---------------------------------------------------------------------------
# Upload
# ---------------------------------------------------------------------------


def upload_to_hf(
    repo_id: str,
    local_dir: Path | str,
    token: str,
    commit_message: str = "Daily sync update",
    repo_type: str = "dataset",
) -> str:
    """Upload a local data directory to a Hugging Face dataset repository.

    Parameters
    ----------
    repo_id : str
        Hugging Face repository identifier.
    local_dir : Path or str
        Local directory whose contents will be uploaded.
    token : str
        Hugging Face API token with write access to the repo.
    commit_message : str
        Commit message for the upload.
    repo_type : str
        Repository type (default ``\"dataset\"``).

    Returns
    -------
    str
        URL of the commit created on Hugging Face.
    """
    logger.info(
        "Uploading %s to %s ... (message: %s)",
        local_dir,
        repo_id,
        commit_message,
    )
    commit_info = upload_folder(
        repo_id=repo_id,
        folder_path=str(local_dir),
        token=token,
        commit_message=commit_message,
        repo_type=repo_type,
    )
    commit_url: str = commit_info.commit_url  # type: ignore[attr-defined]
    logger.info("Upload complete - commit URL: %s", commit_url)
    return commit_url


# ---------------------------------------------------------------------------
# Orchestration pipeline
# ---------------------------------------------------------------------------


def _fetch_new_cases(source_id: str, config_path: Path) -> list[dict[str, Any]]:
    """Fetch new cases from a source using its adapter.

    Parameters
    ----------
    source_id : str
        Source identifier (e.g. ``\"hdc\"``).
    config_path : Path
        Path to the pipeline configuration file.

    Returns
    -------
    list[dict[str, Any]]
        List of fetched case dictionaries.
    """
    adapter = get_adapter(source_id)
    logger.info("Fetching cases from %s (%s)", source_id, SOURCE_REGISTRY[source_id]["name"])
    raw_cases = adapter.fetch()
    logger.info("Fetched %d raw cases from %s", len(raw_cases), source_id)
    return raw_cases


def _process_cases(
    source_id: str,
    raw_cases: list[dict[str, Any]],
    config_path: Path,
) -> list[dict[str, Any]]:
    """Process raw cases through the source adapter.

    Parameters
    ----------
    source_id : str
        Source identifier (e.g. ``\"hdc\"``).
    raw_cases : list[dict[str, Any]]
        Raw fetched cases to process.
    config_path : Path
        Path to the pipeline configuration file.

    Returns
    -------
    list[dict[str, Any]]
        Processed case dictionaries.
    """
    adapter = get_adapter(source_id)
    processed = adapter.process(raw_cases)
    logger.info("Processed %d cases from %s", len(processed), source_id)
    return processed


def _export_data(
    source_id: str,
    cases: list[dict[str, Any]],
    config_path: Path,
) -> Path:
    """Export processed cases to all 4 formats.

    Parameters
    ----------
    source_id : str
        Source identifier (e.g. ``\"hdc\"``).
    cases : list[dict[str, Any]]
        Processed cases to export.
    config_path : Path
        Path to the pipeline configuration file.

    Returns
    -------
    Path
        Path to the exported data directory.
    """
    processed_dir = Path("data/processed")

    exportable_cases = []
    for case in cases:
        exportable_cases.append(ExportableCase(
            case_id=case.get("case_id", f"{source_id}-unknown"),
            source=case.get("source", source_id),
            title=case.get("title", ""),
            date=case.get("date", ""),
            text=case.get("text", ""),
            metadata=case.get("metadata", {}),
        ))

    if exportable_cases:
        results = export_all(exportable_cases, processed_dir)
        for fmt, paths in results.items():
            logger.info("Exported %d files to %s format", len(paths), fmt)
    else:
        logger.info("No cases to export for %s", source_id)

    return processed_dir


def _validate_data(data_dir: Path) -> bool:
    """Validate exported data directory has expected structure.

    Parameters
    ----------
    data_dir : Path
        Directory containing the exported data.

    Returns
    -------
    bool
        ``True`` if all expected sub-directories exist.
    """
    required = ["markdown", "text", "json", "jsonl", "parquet"]
    all_ok = True
    for subdir in required:
        path = data_dir / subdir
        if not path.is_dir():
            logger.warning("Missing export directory: %s", path)
            all_ok = False
        else:
            logger.info("Found export directory: %s", path)
    return all_ok


def sync_pipeline(
    source_id: str,
    config_path: Path | str = None,
    hf_repo_id: str = "edithatogo/corpus-cases-medilegal-nz",
    hf_token: str = "",
) -> dict[str, Any]:
    """Orchestrate a full synchronisation pipeline for one source.

    Steps:
    1. Download the existing snapshot from Hugging Face
    2. Fetch any new cases from source websites via adapter
    3. Process / transform the fetched content via adapter
    4. Export the processed data to the local data directory
    5. Validate the exported data
    6. Upload the updated data directory back to Hugging Face

    Parameters
    ----------
    source_id : str
        Source identifier (e.g. ``\"hdc\"``).
    config_path : Path or str, optional
        Path to the pipeline configuration file.
    hf_repo_id : str
        Hugging Face dataset repository identifier.
    hf_token : str
        Hugging Face API token with write access.

    Returns
    -------
    dict[str, Any]
        Dictionary with keys ``\"source_id\"``, ``\"status\"``, ``\"commit_url\"``,
        and details about each step.
    """
    cfg_path = Path(config_path) if config_path else Path(f"config/{source_id}_pipeline.yaml")
    local_dir = Path("data/processed")

    logger.info("Starting sync pipeline for source=%s repo=%s", source_id, hf_repo_id)

    # Step 1 — Download existing snapshot
    snapshot_ok = False
    if hf_token:
        try:
            download_snapshot(repo_id=hf_repo_id, local_dir=local_dir, token=hf_token)
            snapshot_ok = True
        except Exception:
            logger.exception("Snapshot download failed - proceeding with local data only")
    else:
        logger.info("No HF_TOKEN provided, skipping snapshot download")

    # Step 2 — Fetch new cases via adapter
    fetched = _fetch_new_cases(source_id, cfg_path)

    # Step 3 — Process cases via adapter
    processed = _process_cases(source_id, fetched, cfg_path)

    # Step 4 — Export via format exporters
    export_dir = _export_data(source_id, processed, cfg_path)

    # Step 5 — Validate
    valid = _validate_data(export_dir)

    # Step 6 — Upload
    commit_url = ""
    if valid and hf_token:
        try:
            commit_url = upload_to_hf(
                repo_id=hf_repo_id,
                local_dir=export_dir,
                token=hf_token,
            )
            status = "success"
        except Exception:
            logger.exception("Upload to Hugging Face failed")
            status = "upload_failed"
    elif not hf_token:
        status = "dry_run"
    else:
        status = "validation_failed"

    result: dict[str, Any] = {
        "source_id": source_id,
        "status": status,
        "commit_url": commit_url,
        "steps": {
            "snapshot_downloaded": snapshot_ok,
            "cases_fetched": len(fetched),
            "cases_processed": len(processed),
            "export_dir": str(export_dir),
            "validation_passed": valid,
        },
    }
    logger.info("Sync pipeline finished for %s - status: %s", source_id, status)
    return result


# ---------------------------------------------------------------------------
# CLI entry point (``python -m corpus_cases_medilegal_nz.hf_sync``)
# ---------------------------------------------------------------------------


def main() -> None:
    """Minimal CLI entry point for manual runs.

    Pass a source ID as the first CLI argument (e.g. ``hdc``, ``hpdt``, ``era``)
    or set ``SOURCE_ID`` environment variable to sync a single source.
    If neither is provided, all sources with URLs are synced sequentially.

    Requires ``HF_TOKEN`` environment variable for upload.
    """
    import os
    import sys

    token = os.environ.get("HF_TOKEN", "")
    repo_id = os.environ.get("HF_REPO_ID", "edithatogo/corpus-cases-medilegal-nz")

    # Accept source_id from CLI arg or env var
    source_id = os.environ.get("SOURCE_ID", "")
    if len(sys.argv) > 1:
        source_id = sys.argv[1]

    if source_id:
        # Sync a single source
        if source_id not in SOURCE_REGISTRY:
            available = ", ".join(get_source_ids())
            print(f"Unknown source: {source_id}. Available: {available}")
            sys.exit(1)
        config_path = Path(f"config/{source_id}_pipeline.yaml")
        result = sync_pipeline(
            source_id=source_id,
            config_path=config_path,
            hf_repo_id=repo_id,
            hf_token=token,
        )
        print(f"Sync result for {source_id}: {result}")
    else:
        # Sync all sources
        results = {}
        for sid in get_source_ids():
            if not SOURCE_REGISTRY[sid]["url"]:
                logger.info("Skipping %s (no URL configured)", sid)
                continue
            try:
                config_path = Path(f"config/{sid}_pipeline.yaml")
                results[sid] = sync_pipeline(
                    source_id=sid,
                    config_path=config_path,
                    hf_repo_id=repo_id,
                    hf_token=token,
                )
            except Exception:
                logger.exception("Sync failed for %s", sid)
                results[sid] = {"status": "error"}
        print(f"Sync results: {results}")


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )
    main()
