from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from corpus_cases_medilegal_nz.sources.coronial import CoronialSourceAdapter
from corpus_cases_medilegal_nz.sources.era import EraSourceAdapter
from corpus_cases_medilegal_nz.sources.hdc import HdcSourceAdapter
from corpus_cases_medilegal_nz.sources.hpdt import HpdtSourceAdapter
from corpus_cases_medilegal_nz.sources.human_rights import HumanRightsSourceAdapter
from corpus_cases_medilegal_nz.sources.ipca import IpcaSourceAdapter
from corpus_cases_medilegal_nz.sources.law_commission import LawCommissionSourceAdapter
from corpus_cases_medilegal_nz.sources.moj_courts import MojCourtsSourceAdapter
from corpus_cases_medilegal_nz.sources.moj_tribunals import MojTribunalsSourceAdapter
from corpus_cases_medilegal_nz.sources.ombudsman import OmbudsmanSourceAdapter
from corpus_cases_medilegal_nz.sources.privacy import PrivacySourceAdapter
from corpus_cases_medilegal_nz.sources.royal_commissions import RoyalCommissionsSourceAdapter
from corpus_cases_medilegal_nz.sources.teachers import TeachersSourceAdapter

FIXTURES_ROOT = Path(__file__).parent / "fixtures" / "sources"


def _fixture_html(source_id: str) -> str:
    manifest = json.loads((FIXTURES_ROOT / "fixture_manifest.json").read_text(encoding="utf-8"))
    source_fixture = (
        manifest.get("core_sources", {}).get(source_id) or manifest["extended_sources"][source_id]
    )
    return (FIXTURES_ROOT / source_fixture["html"]).read_text(encoding="utf-8")


def test_hdc_adapter_fetch_parses_fixture_record() -> None:
    adapter = HdcSourceAdapter(source_id="hdc", config_path=Path("config/hdc_pipeline.yaml"))

    with (
        patch("corpus_cases_medilegal_nz.sources.hdc.load_pipeline_config") as mock_load,
        patch("corpus_cases_medilegal_nz.sources.hdc.HdcFetcher") as mock_fetcher_cls,
    ):
        mock_cfg = MagicMock()
        mock_cfg.pipeline.source_url = "https://www.hdc.org.nz/decisions/search-decisions/"
        mock_load.return_value = mock_cfg
        mock_fetcher = MagicMock()
        mock_fetcher.__enter__.return_value = mock_fetcher
        mock_fetcher.fetch_url.return_value = MagicMock(text=_fixture_html("hdc"))
        mock_fetcher_cls.return_value = mock_fetcher

        records = adapter.fetch()

    assert len(records) == 2
    assert records[0]["case_id"] == "HDC26HDC001"
    assert adapter.validate(records) is True


@pytest.mark.parametrize(
    ("source_id", "adapter_cls", "module_path", "config_path", "source_url", "expected_case_id"),
    [
        (
            "hpdt",
            HpdtSourceAdapter,
            "corpus_cases_medilegal_nz.sources.hpdt",
            "config/hpdt_pipeline.yaml",
            "https://www.hpdt.org.nz/Search-Decisions",
            "HPDT26/001",
        ),
        (
            "moj_tribunals",
            MojTribunalsSourceAdapter,
            "corpus_cases_medilegal_nz.sources.moj_tribunals",
            "config/moj_tribunals_pipeline.yaml",
            "https://www.justice.govt.nz/tribunals/",
            "Synthetic Medical Appeal 2026/001",
        ),
        (
            "era",
            EraSourceAdapter,
            "corpus_cases_medilegal_nz.sources.era",
            "config/era_pipeline.yaml",
            "https://www.era.govt.nz/",
            "2026-NZERA-001",
        ),
        (
            "teachers",
            TeachersSourceAdapter,
            "corpus_cases_medilegal_nz.sources.teachers",
            "config/teachers_pipeline.yaml",
            "https://www.teachersdisciplinarytribunal.nz/",
            "TDT-2026-001",
        ),
        (
            "privacy",
            PrivacySourceAdapter,
            "corpus_cases_medilegal_nz.sources.privacy",
            "config/privacy_pipeline.yaml",
            "https://www.privacy.org.nz/resources-and-learning/case-notes-and-court-decisions/",
            "PRIV-2026-001",
        ),
        (
            "human_rights",
            HumanRightsSourceAdapter,
            "corpus_cases_medilegal_nz.sources.human_rights",
            "config/human_rights_pipeline.yaml",
            "https://www.justice.govt.nz/tribunals/human-rights/hrrt-decisions/",
            "HRC-2026-001",
        ),
        (
            "ombudsman",
            OmbudsmanSourceAdapter,
            "corpus_cases_medilegal_nz.sources.ombudsman",
            "config/ombudsman_pipeline.yaml",
            "https://www.ombudsman.parliament.nz/resources",
            "OMB-2026-001",
        ),
        (
            "ipca",
            IpcaSourceAdapter,
            "corpus_cases_medilegal_nz.sources.ipca",
            "config/ipca_pipeline.yaml",
            "https://www.ipca.govt.nz/Site/publications-and-media/Accountability/Archive.aspx",
            "IPCA-2026-001",
        ),
        (
            "law_commission",
            LawCommissionSourceAdapter,
            "corpus_cases_medilegal_nz.sources.law_commission",
            "config/law_commission_pipeline.yaml",
            "https://www.lawcom.govt.nz/our-work",
            "LC-2026-001",
        ),
        (
            "royal_commissions",
            RoyalCommissionsSourceAdapter,
            "corpus_cases_medilegal_nz.sources.royal_commissions",
            "config/royal_commissions_pipeline.yaml",
            "https://www.waitangitribunal.govt.nz/en/publications/tribunal-reports",
            "RC-2026-001",
        ),
        (
            "coronial",
            CoronialSourceAdapter,
            "corpus_cases_medilegal_nz.sources.coronial",
            "config/coronial_pipeline.yaml",
            "https://coronialservices.justice.govt.nz/",
            "COR-2026-001",
        ),
        (
            "moj_courts",
            MojCourtsSourceAdapter,
            "corpus_cases_medilegal_nz.sources.moj_courts",
            "config/moj_courts_pipeline.yaml",
            "https://www.justice.govt.nz/courts/decisions/jdo/",
            "MOJ-COURTS-2026-001",
        ),
    ],
)
def test_requests_adapter_fetch_parses_fixture_record(
    source_id: str,
    adapter_cls: type[
        HpdtSourceAdapter
        | MojTribunalsSourceAdapter
        | EraSourceAdapter
        | TeachersSourceAdapter
        | PrivacySourceAdapter
        | HumanRightsSourceAdapter
        | OmbudsmanSourceAdapter
        | IpcaSourceAdapter
        | LawCommissionSourceAdapter
        | RoyalCommissionsSourceAdapter
        | CoronialSourceAdapter
        | MojCourtsSourceAdapter
    ],
    module_path: str,
    config_path: str,
    source_url: str,
    expected_case_id: str,
) -> None:
    adapter = adapter_cls(source_id=source_id, config_path=Path(config_path))

    with patch(f"{module_path}.load_pipeline_config") as mock_load:
        mock_cfg = MagicMock()
        mock_cfg.pipeline.source_url = source_url
        mock_load.return_value = mock_cfg

        with patch.object(adapter, "_build_session") as mock_build_session:
            mock_session = MagicMock()
            mock_response = MagicMock(text=_fixture_html(source_id))
            mock_response.raise_for_status.return_value = None
            mock_session.get.return_value = mock_response
            mock_build_session.return_value = mock_session

            records = adapter.fetch()

    assert len(records) == 2
    assert records[0]["case_id"] == expected_case_id
    assert records[0]["source"] == source_id
    assert adapter.validate(records) is True
