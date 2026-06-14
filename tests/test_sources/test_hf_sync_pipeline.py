"""Tests for the wired hf_sync.py pipeline functions."""
from __future__ import annotations

from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

from corpus_cases_medilegal_nz.hf_sync import (
    _fetch_new_cases,
    _process_cases,
    _export_data,
    _validate_data,
    sync_pipeline,
    download_snapshot,
    upload_to_hf,
    main,
)


# ===========================================================================
# download_snapshot
# ===========================================================================

class TestDownloadSnapshot:
    """Tests for download_snapshot()."""

    def test_returns_path(self):
        """download_snapshot returns a Path."""
        with patch("corpus_cases_medilegal_nz.hf_sync.snapshot_download") as mock_snap:
            mock_snap.return_value = None
            result = download_snapshot(
                repo_id="test/repo",
                local_dir=Path("data/processed"),
                token=None,
            )
            assert isinstance(result, Path)

    def test_creates_local_dir(self):
        """download_snapshot creates the local directory."""
        with patch("corpus_cases_medilegal_nz.hf_sync.snapshot_download") as mock_snap:
            mock_snap.return_value = None
            with patch("corpus_cases_medilegal_nz.hf_sync.Path.mkdir") as mock_mkdir:
                download_snapshot(
                    repo_id="test/repo",
                    local_dir=Path("data/processed"),
                    token=None,
                )
                mock_mkdir.assert_called_once_with(parents=True, exist_ok=True)

    def test_calls_snapshot_download(self):
        """download_snapshot calls huggingface_hub.snapshot_download."""
        with patch("corpus_cases_medilegal_nz.hf_sync.snapshot_download") as mock_snap:
            mock_snap.return_value = None
            download_snapshot(
                repo_id="test/repo",
                local_dir=Path("data/processed"),
                token="hf_abc123",
            )
            mock_snap.assert_called_once_with(
                repo_id="test/repo",
                repo_type="dataset",
                local_dir=str(Path("data/processed")),
                token="hf_abc123",
                resume_download=True,
            )


# ===========================================================================
# upload_to_hf
# ===========================================================================

class TestUploadToHf:
    """Tests for upload_to_hf()."""

    def test_returns_commit_url(self):
        """upload_to_hf returns a commit URL string."""
        with patch("corpus_cases_medilegal_nz.hf_sync.upload_folder") as mock_upload:
            mock_info = MagicMock()
            mock_info.commit_url = "https://huggingface.co/commits/abc"
            mock_upload.return_value = mock_info

            result = upload_to_hf(
                repo_id="test/repo",
                local_dir=Path("data/processed"),
                token="hf_abc123",
            )
            assert isinstance(result, str)

    def test_calls_upload_folder(self):
        """upload_to_hf calls huggingface_hub.upload_folder."""
        with patch("corpus_cases_medilegal_nz.hf_sync.upload_folder") as mock_upload:
            mock_info = MagicMock()
            mock_info.commit_url = "https://huggingface.co/commits/abc"
            mock_upload.return_value = mock_info

            result = upload_to_hf(
                repo_id="test/repo",
                local_dir=Path("data/processed"),
                token="hf_abc123",
                commit_message="Daily sync update",
            )
            mock_upload.assert_called_once_with(
                repo_id="test/repo",
                folder_path=str(Path("data/processed")),
                token="hf_abc123",
                commit_message="Daily sync update",
                repo_type="dataset",
            )
            assert result == "https://huggingface.co/commits/abc"

# ===========================================================================
# _fetch_new_cases
# ===========================================================================

class TestFetchNewCases:
    """Tests for _fetch_new_cases()."""

    @patch("corpus_cases_medilegal_nz.hf_sync.get_adapter")
    def test_returns_list(self, mock_get_adapter):
        """_fetch_new_cases returns a list."""
        mock_adapter = MagicMock()
        mock_adapter.fetch.return_value = []
        mock_get_adapter.return_value = mock_adapter
        result = _fetch_new_cases("hdc", Path("config/hdc_pipeline.yaml"))
        assert isinstance(result, list)

    @patch("corpus_cases_medilegal_nz.hf_sync.get_adapter")
    def test_calls_adapter_fetch(self, mock_get_adapter):
        """_fetch_new_cases calls adapter.fetch()."""
        mock_adapter = MagicMock()
        mock_adapter.fetch.return_value = [{"case_id": "HDC-001"}]
        mock_get_adapter.return_value = mock_adapter
        result = _fetch_new_cases("hdc", Path("config/hdc_pipeline.yaml"))
        mock_get_adapter.assert_called_once_with("hdc")
        mock_adapter.fetch.assert_called_once()
        assert result == [{"case_id": "HDC-001"}]

    @patch("corpus_cases_medilegal_nz.hf_sync.get_adapter")
    def test_empty_for_hdc(self, mock_get_adapter):
        """HDC fetch returns empty list (stub until nlp_policy_nz)."""
        mock_adapter = MagicMock()
        mock_adapter.fetch.return_value = []
        mock_get_adapter.return_value = mock_adapter
        result = _fetch_new_cases("hdc", Path("config/hdc_pipeline.yaml"))
        assert len(result) == 0


# ===========================================================================
# _process_cases
# ===========================================================================

class TestProcessCases:
    """Tests for _process_cases()."""

    @patch("corpus_cases_medilegal_nz.hf_sync.get_adapter")
    def test_sets_source(self, mock_get_adapter):
        """_process_cases sets source field via adapter."""
        mock_adapter = MagicMock()
        mock_adapter.process.return_value = [{"case_id": "test", "source": "hdc"}]
        mock_get_adapter.return_value = mock_adapter
        result = _process_cases("hdc", [{"case_id": "test"}], Path("config/hdc_pipeline.yaml"))
        assert result[0]["source"] == "hdc"

    @patch("corpus_cases_medilegal_nz.hf_sync.get_adapter")
    def test_calls_adapter_process(self, mock_get_adapter):
        """_process_cases delegates to adapter.process()."""
        mock_adapter = MagicMock()
        mock_adapter.process.return_value = []
        mock_get_adapter.return_value = mock_adapter
        raw = [{"case_id": "test", "text": "hello"}]
        _process_cases("hdc", raw, Path("config/hdc_pipeline.yaml"))
        mock_adapter.process.assert_called_once_with(raw)


# ===========================================================================
# _export_data
# ===========================================================================

class TestExportData:
    """Tests for _export_data()."""

    @patch("corpus_cases_medilegal_nz.hf_sync.export_all")
    def test_returns_path(self, mock_export):
        """_export_data returns a Path."""
        mock_export.return_value = {"markdown": [Path("out.md")]}
        result = _export_data("hdc", [], Path("config/hdc_pipeline.yaml"))
        assert isinstance(result, Path)

    @patch("corpus_cases_medilegal_nz.hf_sync.export_all")
    def test_returns_expected_path(self, mock_export):
        """_export_data returns the data/processed directory."""
        mock_export.return_value = {"markdown": [Path("out.md")]}
        result = _export_data("hdc", [], Path("config/hdc_pipeline.yaml"))
        assert "data" in str(result)
        assert "processed" in str(result)

    @patch("corpus_cases_medilegal_nz.hf_sync.export_all")
    def test_calls_export_all_with_cases(self, mock_export):
        """_export_data calls export_all when cases provided."""
        mock_export.return_value = {"markdown": [Path("out.md")]}
        cases = [{"case_id": "HDC-001", "text": "hello", "source": "hdc",
                  "title": "T", "date": "2024-01-01", "metadata": {}}]
        result = _export_data("hdc", cases, Path("config/hdc_pipeline.yaml"))
        mock_export.assert_called_once()

    @patch("corpus_cases_medilegal_nz.hf_sync.export_all")
    def test_skips_export_when_no_cases(self, mock_export):
        """_export_data skips export_all when no cases."""
        result = _export_data("hdc", [], Path("config/hdc_pipeline.yaml"))
        mock_export.assert_not_called()
        assert isinstance(result, Path)


# ===========================================================================
# _validate_data
# ===========================================================================

class TestValidateData:
    """Tests for _validate_data()."""

    def test_returns_bool(self):
        """_validate_data returns a bool."""
        result = _validate_data(Path("data/processed"))
        assert isinstance(result, bool)

    def test_validates_structure(self):
        """_validate_data checks export directory structure."""
        result = _validate_data(Path("data/processed"))
        assert isinstance(result, bool)


# ===========================================================================
# sync_pipeline
# ===========================================================================

class TestSyncPipeline:
    """Tests for sync_pipeline()."""

    @patch("corpus_cases_medilegal_nz.hf_sync.download_snapshot")
    @patch("corpus_cases_medilegal_nz.hf_sync._fetch_new_cases")
    @patch("corpus_cases_medilegal_nz.hf_sync._process_cases")
    @patch("corpus_cases_medilegal_nz.hf_sync._export_data")
    @patch("corpus_cases_medilegal_nz.hf_sync._validate_data")
    @patch("corpus_cases_medilegal_nz.hf_sync.upload_to_hf")
    def test_returns_dict(self, mock_upload, mock_validate, mock_export,
                          mock_process, mock_fetch, mock_download):
        """sync_pipeline returns a dict with expected keys."""
        mock_download.return_value = Path("data/processed")
        mock_fetch.return_value = []
        mock_process.return_value = []
        mock_export.return_value = Path("data/processed")
        mock_validate.return_value = True
        mock_upload.return_value = "https://huggingface.co/commits/abc"

        result = sync_pipeline(
            source_id="hdc",
            config_path=Path("config/hdc_pipeline.yaml"),
            hf_repo_id="test/repo",
            hf_token="hf_abc123",
        )
        assert isinstance(result, dict)
        assert "source_id" in result
        assert "status" in result
        assert "commit_url" in result
        assert "steps" in result

    @patch("corpus_cases_medilegal_nz.hf_sync.download_snapshot")
    @patch("corpus_cases_medilegal_nz.hf_sync._fetch_new_cases")
    @patch("corpus_cases_medilegal_nz.hf_sync._process_cases")
    @patch("corpus_cases_medilegal_nz.hf_sync._export_data")
    @patch("corpus_cases_medilegal_nz.hf_sync._validate_data")
    @patch("corpus_cases_medilegal_nz.hf_sync.upload_to_hf")
    def test_success_status(self, mock_upload, mock_validate, mock_export,
                            mock_process, mock_fetch, mock_download):
        """sync_pipeline returns success status."""
        mock_download.return_value = Path("data/processed")
        mock_fetch.return_value = []
        mock_process.return_value = []
        mock_export.return_value = Path("data/processed")
        mock_validate.return_value = True
        mock_upload.return_value = "https://huggingface.co/commits/abc"

        result = sync_pipeline(
            source_id="hdc",
            config_path=Path("config/hdc_pipeline.yaml"),
            hf_repo_id="test/repo",
            hf_token="hf_abc123",
        )
        assert result["status"] == "success"
        assert result["source_id"] == "hdc"

    @patch("corpus_cases_medilegal_nz.hf_sync.download_snapshot")
    @patch("corpus_cases_medilegal_nz.hf_sync._fetch_new_cases")
    @patch("corpus_cases_medilegal_nz.hf_sync._process_cases")
    @patch("corpus_cases_medilegal_nz.hf_sync._export_data")
    @patch("corpus_cases_medilegal_nz.hf_sync._validate_data")
    @patch("corpus_cases_medilegal_nz.hf_sync.upload_to_hf")
    def test_dry_run_status(self, mock_upload, mock_validate, mock_export,
                            mock_process, mock_fetch, mock_download):
        """sync_pipeline returns dry_run status when no token."""
        mock_fetch.return_value = []
        mock_process.return_value = []
        mock_export.return_value = Path("data/processed")
        mock_validate.return_value = True

        result = sync_pipeline(
            source_id="hdc",
            config_path=Path("config/hdc_pipeline.yaml"),
            hf_repo_id="test/repo",
            hf_token="",
        )
        assert result["status"] == "dry_run"
        mock_download.assert_not_called()
        mock_upload.assert_not_called()


    @patch("corpus_cases_medilegal_nz.hf_sync.download_snapshot")
    @patch("corpus_cases_medilegal_nz.hf_sync._fetch_new_cases")
    @patch("corpus_cases_medilegal_nz.hf_sync._process_cases")
    @patch("corpus_cases_medilegal_nz.hf_sync._export_data")
    @patch("corpus_cases_medilegal_nz.hf_sync._validate_data")
    @patch("corpus_cases_medilegal_nz.hf_sync.upload_to_hf")
    def test_steps_structure(self, mock_upload, mock_validate, mock_export,
                             mock_process, mock_fetch, mock_download):
        """sync_pipeline steps contain expected keys."""
        mock_download.return_value = Path("data/processed")
        mock_fetch.return_value = []
        mock_process.return_value = []
        mock_export.return_value = Path("data/processed")
        mock_validate.return_value = True
        mock_upload.return_value = "https://huggingface.co/commits/abc"

        result = sync_pipeline(
            source_id="hdc",
            config_path=Path("config/hdc_pipeline.yaml"),
            hf_repo_id="test/repo",
            hf_token="hf_abc123",
        )
        steps = result["steps"]
        assert "snapshot_downloaded" in steps
        assert "cases_fetched" in steps
        assert "cases_processed" in steps
        assert "export_dir" in steps
        assert "validation_passed" in steps

    @patch("corpus_cases_medilegal_nz.hf_sync.download_snapshot")
    @patch("corpus_cases_medilegal_nz.hf_sync._fetch_new_cases")
    @patch("corpus_cases_medilegal_nz.hf_sync._process_cases")
    @patch("corpus_cases_medilegal_nz.hf_sync._export_data")
    @patch("corpus_cases_medilegal_nz.hf_sync._validate_data")
    @patch("corpus_cases_medilegal_nz.hf_sync.upload_to_hf")
    def test_download_failure_continues(self, mock_upload, mock_validate,
                                        mock_export, mock_process, mock_fetch,
                                        mock_download):
        """sync_pipeline continues when snapshot download fails."""
        mock_download.side_effect = RuntimeError("Download failed")
        mock_fetch.return_value = []
        mock_process.return_value = []
        mock_export.return_value = Path("data/processed")
        mock_validate.return_value = True
        mock_upload.return_value = "https://huggingface.co/commits/abc"

        result = sync_pipeline(
            source_id="hdc",
            config_path=Path("config/hdc_pipeline.yaml"),
            hf_repo_id="test/repo",
            hf_token="hf_abc123",
        )
        assert result["steps"]["snapshot_downloaded"] is False
        assert result["status"] == "success"

    @patch("corpus_cases_medilegal_nz.hf_sync.download_snapshot")
    @patch("corpus_cases_medilegal_nz.hf_sync._fetch_new_cases")
    @patch("corpus_cases_medilegal_nz.hf_sync._process_cases")
    @patch("corpus_cases_medilegal_nz.hf_sync._export_data")
    @patch("corpus_cases_medilegal_nz.hf_sync._validate_data")
    @patch("corpus_cases_medilegal_nz.hf_sync.upload_to_hf")
    def test_validation_failure_skips_upload(self, mock_upload, mock_validate,
                                             mock_export, mock_process,
                                             mock_fetch, mock_download):
        """sync_pipeline skips upload when validation fails."""
        mock_download.return_value = Path("data/processed")
        mock_fetch.return_value = []
        mock_process.return_value = []
        mock_export.return_value = Path("data/processed")
        mock_validate.return_value = False

        result = sync_pipeline(
            source_id="hdc",
            config_path=Path("config/hdc_pipeline.yaml"),
            hf_repo_id="test/repo",
            hf_token="hf_abc123",
        )
        assert result["status"] == "validation_failed"
        mock_upload.assert_not_called()

