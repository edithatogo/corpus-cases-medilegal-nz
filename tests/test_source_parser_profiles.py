from __future__ import annotations

from corpus_cases_medilegal_nz.source_maturity import HIGH_RISK_GENERIC_PARSER_SOURCES
from corpus_cases_medilegal_nz.source_parser_profiles import (
    SOURCE_SPECIFIC_PARSER_PROFILES,
    parse_source_specific_listing_html,
)


def test_high_risk_sources_have_source_specific_profiles() -> None:
    assert set(SOURCE_SPECIFIC_PARSER_PROFILES) == HIGH_RISK_GENERIC_PARSER_SOURCES


def test_source_specific_parser_attaches_profile_metadata() -> None:
    html = """
    <html><body>
      <article>
        <h2>Court decision</h2>
        <a href="/courts/decisions/jdo/2026/example/">MOJ-COURTS-2026-999</a>
        <time datetime="2026-07-01">1 July 2026</time>
        <p>Decision summary.</p>
      </article>
    </body></html>
    """

    records = parse_source_specific_listing_html(
        source_id="moj_courts",
        url="https://www.justice.govt.nz/courts/decisions/jdo/",
        html=html,
    )

    assert records[0]["metadata"]["parser_profile_id"] == "moj_courts_jdo_v1"
    assert "source_parser_profiles" in records[0]["metadata"]["parser_name"]
