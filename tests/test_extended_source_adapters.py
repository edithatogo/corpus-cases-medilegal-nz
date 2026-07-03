from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from corpus_cases_medilegal_nz.sources import get_adapter
from corpus_cases_medilegal_nz.sources.coronial import CoronialSourceAdapter
from corpus_cases_medilegal_nz.sources.human_rights import HumanRightsSourceAdapter
from corpus_cases_medilegal_nz.sources.ipca import IpcaSourceAdapter
from corpus_cases_medilegal_nz.sources.law_commission import LawCommissionSourceAdapter
from corpus_cases_medilegal_nz.sources.moj_courts import MojCourtsSourceAdapter
from corpus_cases_medilegal_nz.sources.ombudsman import OmbudsmanSourceAdapter
from corpus_cases_medilegal_nz.sources.royal_commissions import RoyalCommissionsSourceAdapter
from corpus_cases_medilegal_nz.sources.privacy import PrivacySourceAdapter

EXTENDED_SOURCE_CASES = [
    (
        "privacy",
        PrivacySourceAdapter,
        "config/privacy_pipeline.yaml",
        "https://www.privacy.org.nz/resources-and-learning/case-notes-and-court-decisions/",
        "Privacy Commissioner",
        "PRIV-2026-001",
        "Privacy Commissioner decision",
        "https://www.privacy.org.nz/resources-and-learning/case-notes-and-court-decisions/2026/priv-2026-001/",
    ),
    (
        "human_rights",
        HumanRightsSourceAdapter,
        "config/human_rights_pipeline.yaml",
        "https://www.justice.govt.nz/tribunals/human-rights/hrrt-decisions/",
        "Human Rights Commission/Tribunal",
        "HRC-2026-001",
        "Human Rights Commission/Tribunal decision",
        "https://www.justice.govt.nz/tribunals/human-rights/hrrt-decisions/2026/hrc-2026-001/",
    ),
    (
        "ombudsman",
        OmbudsmanSourceAdapter,
        "config/ombudsman_pipeline.yaml",
        "https://www.ombudsman.parliament.nz/resources",
        "Ombudsman Reports",
        "OMB-2026-001",
        "Ombudsman report",
        "https://www.ombudsman.parliament.nz/resources/2026/omb-2026-001/",
    ),
    (
        "ipca",
        IpcaSourceAdapter,
        "config/ipca_pipeline.yaml",
        "https://www.ipca.govt.nz/Site/publications-and-media/Accountability/Archive.aspx",
        "Independent Police Conduct Authority",
        "IPCA-2026-001",
        "Independent Police Conduct Authority report",
        "https://www.ipca.govt.nz/Site/publications-and-media/Accountability/Archive.aspx?report=ipca-2026-001",
    ),
    (
        "law_commission",
        LawCommissionSourceAdapter,
        "config/law_commission_pipeline.yaml",
        "https://www.lawcom.govt.nz/our-work",
        "Law Commission Reports",
        "LC-2026-001",
        "Law Commission report",
        "https://www.lawcom.govt.nz/our-work/2026/lc-2026-001/",
    ),
    (
        "royal_commissions",
        RoyalCommissionsSourceAdapter,
        "config/royal_commissions_pipeline.yaml",
        "https://www.waitangitribunal.govt.nz/en/publications/tribunal-reports",
        "Royal Commissions & Waitangi Tribunal",
        "RC-2026-001",
        "Royal Commission report",
        "https://www.waitangitribunal.govt.nz/en/publications/tribunal-reports/wai-1040/",
    ),
    (
        "coronial",
        CoronialSourceAdapter,
        "config/coronial_pipeline.yaml",
        "https://coronialservices.justice.govt.nz/",
        "Coronial Decisions",
        "COR-2026-001",
        "Coronial finding",
        "https://coronialservices.justice.govt.nz/findings-and-recommendations/2026/cor-2026-001/",
    ),
    (
        "moj_courts",
        MojCourtsSourceAdapter,
        "config/moj_courts_pipeline.yaml",
        "https://www.justice.govt.nz/courts/decisions/jdo/",
        "Ministry of Justice Court Cases",
        "MOJ-COURTS-2026-001",
        "Court decision",
        "https://www.justice.govt.nz/courts/decisions/jdo/2026/moj-courts-2026-001/",
    ),
]


def _listing_html(*, title: str, identifier: str, href: str, date: str, body: str) -> str:
    return f"""
    <!doctype html>
    <html lang="en">
      <body>
        <main>
          <article>
            <h1>{title}</h1>
            <h2>{title}</h2>
            <a href="{href}">{identifier}</a>
            <time datetime="{date}">{date}</time>
            <p>{body}</p>
          </article>
        </main>
      </body>
    </html>
    """


@pytest.mark.parametrize(
    ("source_id", "adapter_cls", "config_path", "source_url", "source_name", "case_id", "title", "href"),
    EXTENDED_SOURCE_CASES,
)
def test_extended_source_adapters_fetch_and_validate(
    source_id: str,
    adapter_cls: type[
        PrivacySourceAdapter
        | HumanRightsSourceAdapter
        | OmbudsmanSourceAdapter
        | IpcaSourceAdapter
        | LawCommissionSourceAdapter
    ],
    config_path: str,
    source_url: str,
    source_name: str,
    case_id: str,
    title: str,
    href: str,
) -> None:
    adapter = adapter_cls(source_id=source_id, config_path=Path(config_path))
    html = _listing_html(
        title=title,
        identifier=case_id,
        href=href,
        date="2026-07-01",
        body=f"Synthetic {source_name} fixture summary.",
    )

    with patch(f"{adapter_cls.__module__}.load_pipeline_config") as mock_load:
        mock_cfg = MagicMock()
        mock_cfg.pipeline.source_url = source_url
        mock_load.return_value = mock_cfg

        with patch.object(adapter, "_build_session") as mock_build_session:
            mock_session = MagicMock()
            mock_response = MagicMock(text=html)
            mock_response.raise_for_status.return_value = None
            mock_session.get.return_value = mock_response
            mock_build_session.return_value = mock_session

            records = adapter.fetch()

    assert len(records) == 1
    record = records[0]
    assert record["case_id"] == case_id
    assert record["source"] == source_id
    assert record["title"] == title
    assert record["metadata"]["source_name"] == source_name
    assert adapter.validate(records) is True


@pytest.mark.parametrize(
    ("source_id", "expected_cls"),
    [
        ("privacy", PrivacySourceAdapter),
        ("human_rights", HumanRightsSourceAdapter),
        ("ombudsman", OmbudsmanSourceAdapter),
        ("ipca", IpcaSourceAdapter),
        ("law_commission", LawCommissionSourceAdapter),
        ("royal_commissions", RoyalCommissionsSourceAdapter),
        ("coronial", CoronialSourceAdapter),
        ("moj_courts", MojCourtsSourceAdapter),
    ],
)
def test_get_adapter_dispatches_extended_sources(source_id: str, expected_cls: type[object]) -> None:
    adapter = get_adapter(source_id)
    assert isinstance(adapter, expected_cls)
    assert adapter.source_id == source_id
