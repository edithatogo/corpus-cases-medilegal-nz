"""Source listing parsers for NZ medical-legal corpus adapters."""

from __future__ import annotations

import hashlib
import re
from datetime import UTC, datetime
from typing import Any
from urllib.parse import urljoin

from bs4 import BeautifulSoup, Tag

from corpus_cases_medilegal_nz.parser_contract import (
    PARSER_CONTRACT_VERSION,
    validate_parser_input,
    validate_parser_records,
)

SOURCE_NAMES = {
    "hdc": "Health and Disability Commissioner",
    "hpdt": "Health Practitioners Disciplinary Tribunal",
    "moj_tribunals": "Ministry of Justice Tribunals",
    "era": "Employment Relations Authority",
    "teachers": "Teachers Disciplinary Tribunal",
}

SOURCE_DEFAULT_TITLE = {
    "hdc": "Health and Disability Commissioner decision",
    "hpdt": "Health Practitioners Disciplinary Tribunal decision",
    "moj_tribunals": "Ministry of Justice tribunal decision",
    "era": "Employment Relations Authority determination",
    "teachers": "Teachers Disciplinary Tribunal decision",
}

JsonObject = dict[str, Any]


def parse_source_listing_html(
    *,
    source_id: str,
    url: str,
    html: str,
    retrieved_at: str | None = None,
) -> list[JsonObject]:
    """Parse one source listing page into contract-valid corpus records."""
    payload = validate_parser_input(
        {
            "source_id": source_id,
            "url": url,
            "content": html,
            "content_type": "text/html",
        }
    )
    retrieved = retrieved_at or datetime.now(UTC).replace(microsecond=0).isoformat()
    raw_sha256 = hashlib.sha256(str(payload["content"]).encode("utf-8")).hexdigest()
    soup = BeautifulSoup(str(payload["content"]), "html.parser")
    records = [
        _build_record(
            source_id=source_id,
            listing_url=url,
            element=element,
            retrieved_at=retrieved,
            raw_sha256=raw_sha256,
        )
        for element in _candidate_elements(soup)
    ]
    return validate_parser_records(records, source_id=source_id)


def _candidate_elements(soup: BeautifulSoup) -> list[Tag]:
    elements: list[Tag] = []
    for element in soup.find_all(["article", "li", "tr"]):
        if not isinstance(element, Tag):
            continue
        if element.find("a", href=True) and element.find("time"):
            elements.append(element)
    return elements


def _build_record(
    *,
    source_id: str,
    listing_url: str,
    element: Tag,
    retrieved_at: str,
    raw_sha256: str,
) -> JsonObject:
    link = element.find("a", href=True)
    time_tag = element.find("time")
    if not isinstance(link, Tag) or not isinstance(time_tag, Tag):
        msg = "candidate element must include a decision link and time element"
        raise ValueError(msg)

    href = str(link.get("href", "")).strip()
    decision_url = urljoin(listing_url, href)
    identifier = _clean_text(link.get_text(" ", strip=True)) or PathFallback.from_url(decision_url)
    date = _clean_text(str(time_tag.get("datetime") or time_tag.get_text(" ", strip=True)))
    title = _extract_title(element, identifier, source_id)
    body_text = _extract_body_text(element, title, identifier, date)

    return {
        "case_id": identifier,
        "source": source_id,
        "title": title,
        "date": date,
        "text": body_text,
        "url": decision_url,
        "citation": identifier,
        "commissioner": "" if source_id == "hdc" else None,
        "metadata": {
            "url": decision_url,
            "retrieved_at": retrieved_at,
            "parser_name": "corpus_cases_medilegal_nz.medilegal_parser.parse_source_listing_html",
            "parser_version": PARSER_CONTRACT_VERSION,
            "raw_sha256": raw_sha256,
            "decision_link": href,
            "listing_url": listing_url,
            "source_name": SOURCE_NAMES.get(source_id, source_id),
        },
    }


def _extract_title(element: Tag, identifier: str, source_id: str) -> str:
    for selector in ("h2", "h3", "h1"):
        title_tag = element.find(selector)
        if isinstance(title_tag, Tag):
            title = _clean_text(title_tag.get_text(" ", strip=True))
            if title and title != identifier:
                return title
    heading = element.find_parent(["main", "section", "body"])
    if isinstance(heading, Tag):
        h1 = heading.find("h1")
        if isinstance(h1, Tag):
            title = _clean_text(h1.get_text(" ", strip=True))
            if title:
                return title
    return SOURCE_DEFAULT_TITLE.get(source_id, "Medical-legal decision")


def _extract_body_text(element: Tag, title: str, identifier: str, date: str) -> str:
    paragraphs = [
        _clean_text(paragraph.get_text(" ", strip=True))
        for paragraph in element.find_all("p")
        if isinstance(paragraph, Tag)
    ]
    body = " ".join(paragraph for paragraph in paragraphs if paragraph)
    if body:
        return body
    return _clean_text(" ".join(part for part in (title, identifier, date) if part))


def _clean_text(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()


class PathFallback:
    """Fallback identifier builder for links with no text."""

    @staticmethod
    def from_url(url: str) -> str:
        """Return a stable non-empty identifier from a URL path."""
        candidate = url.rstrip("/").rsplit("/", maxsplit=1)[-1]
        return candidate or hashlib.sha256(url.encode("utf-8")).hexdigest()[:12]
