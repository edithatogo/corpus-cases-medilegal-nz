from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.sync_riopa_project import (  # noqa: E402
    REPO_PROJECT,
    RIOPA_PROJECT,
    SUB_ISSUES,
    build_sync_plan,
    issue_body,
    parse_markers,
)


def _issue(number: int, marker_id: str, title: str, state: str = "CLOSED") -> dict:
    return {
        "number": number,
        "title": title,
        "state": state,
        "body": issue_body(next(spec for spec in SUB_ISSUES if spec.marker_id == marker_id)),
    }


def _project_item(number: int, status: str, mirror_source: str | None = None) -> dict:
    item = {
        "id": f"item-{number}",
        "content": {"number": number},
        "status": status,
    }
    if mirror_source is not None:
        item["mirror source"] = mirror_source
    return item


def test_parse_markers_extracts_stable_metadata() -> None:
    markers = parse_markers(
        """
        <!-- parent-issue: 1 -->
        <!-- riopa-subissue-id: huggingface-remote-proof -->
        <!-- conductor-track-id: monthly_dynamic_archive_publication_20260701 -->
        """
    )

    assert markers["parent-issue"] == "1"
    assert markers["riopa-subissue-id"] == "huggingface-remote-proof"
    assert markers["conductor-track-id"] == "monthly_dynamic_archive_publication_20260701"


def test_build_sync_plan_reports_in_sync_state() -> None:
    issues = []
    riopa_items = []
    repo_items = []
    for index, spec in enumerate(SUB_ISSUES, start=2):
        state = "OPEN" if spec.status == "in_progress" else "CLOSED"
        status = "In Progress" if spec.status == "in_progress" else "Done"
        issues.append(_issue(index, spec.marker_id, spec.title, state=state))
        riopa_items.append(_project_item(index, status, mirror_source="other"))
        repo_items.append(_project_item(index, status))

    plan = build_sync_plan(issues, riopa_items, repo_items)

    assert plan["status"] == "in_sync"
    assert plan["actions"] == []
    assert plan["duplicate_markers"] == {}


def test_build_sync_plan_detects_missing_issue_and_project_drift() -> None:
    first = SUB_ISSUES[0]
    issues = [_issue(2, first.marker_id, "Wrong title", state="OPEN")]
    riopa_items = [_project_item(2, "Todo", mirror_source=None)]
    repo_items: list[dict] = []

    plan = build_sync_plan(issues, riopa_items, repo_items)
    actions = {
        (action["action"], action.get("marker_id"), action.get("project"))
        for action in plan["actions"]
    }

    assert plan["status"] == "drift"
    assert ("update_issue_title", None, None) in actions
    assert ("close_issue", None, None) in actions
    assert ("set_status", None, RIOPA_PROJECT) in actions
    assert ("set_mirror_source", None, RIOPA_PROJECT) in actions
    assert ("add_to_project", None, REPO_PROJECT) in actions
    assert any(action["action"] == "create_issue" for action in plan["actions"])


def test_build_sync_plan_blocks_duplicate_markers() -> None:
    first = SUB_ISSUES[0]
    issues = [
        _issue(2, first.marker_id, first.title),
        _issue(9, first.marker_id, first.title),
    ]

    plan = build_sync_plan(issues, [], [])

    assert plan["status"] == "blocked"
    assert plan["duplicate_markers"] == {first.marker_id: [2, 9]}
