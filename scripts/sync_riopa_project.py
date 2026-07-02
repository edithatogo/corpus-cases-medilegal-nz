"""Synchronize medilegal Conductor issue markers with GitHub Projects."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

OWNER = "edithatogo"
REPO = "corpus-cases-medilegal-nz"
REPOSITORY = f"{OWNER}/{REPO}"
PARENT_ISSUE = 1
RIOPA_PROJECT = "Rare Insights on Open Policy from Aotearoa"
REPO_PROJECT = "corpus-cases-medilegal-nz Archive Roadmap"
RIOPA_PROJECT_ID = "PVT_kwHOAOYc4M4BcJFF"
REPO_PROJECT_ID = "PVT_kwHOAOYc4M4BcLDo"
RIOPA_STATUS_FIELD_ID = "PVTSSF_lAHOAOYc4M4BcJFFzhW0BX4"
RIOPA_MIRROR_FIELD_ID = "PVTSSF_lAHOAOYc4M4BcJFFzhW0HKg"
REPO_STATUS_FIELD_ID = "PVTSSF_lAHOAOYc4M4BcLDozhW1yOo"
STATUS_DONE_OPTION_ID = "98236657"
STATUS_IN_PROGRESS_OPTION_ID = "47fc9ee4"
RIOPA_MIRROR_OTHER_OPTION_ID = "a77f89f8"
PARENT_TRACK_ID = "monthly_dynamic_archive_publication_20260701"
SYNC_TRACK_ID = "github_riopa_project_synchronisation_20260701"
MARKER_PATTERN = re.compile(r"<!--\s*([a-zA-Z0-9_-]+):\s*([^>]+?)\s*-->")

JsonObject = dict[str, Any]


@dataclass(frozen=True)
class SubIssueSpec:
    """Desired RIOPA sub-issue state."""

    marker_id: str
    title: str
    summary: str
    status: str
    evidence: str

    @property
    def status_option_id(self) -> str:
        """Return the GitHub Projects status option for this issue."""
        if self.status == "in_progress":
            return STATUS_IN_PROGRESS_OPTION_ID
        return STATUS_DONE_OPTION_ID

    @property
    def should_be_closed(self) -> bool:
        """Return whether the issue should be closed as completed proof."""
        return self.status == "completed"


SUB_ISSUES = [
    SubIssueSpec(
        marker_id="huggingface-remote-proof",
        title="Hugging Face remote proof",
        summary="Track Hugging Face publication/readback evidence for the monthly archive.",
        status="completed",
        evidence=(
            "Existing evidence: issue #1 comment "
            "https://github.com/edithatogo/corpus-cases-medilegal-nz/issues/1#issuecomment-4861246629 "
            "and conductor/tracks/monthly_dynamic_archive_publication_20260701/"
            "phase8_huggingface_publication_evidence.md."
        ),
    ),
    SubIssueSpec(
        marker_id="zenodo-draft-proof",
        title="Zenodo draft and new-version proof",
        summary="Track Zenodo draft/new-version upload evidence and draft-only publication boundary.",
        status="completed",
        evidence=(
            "Existing evidence: issue #1 comment "
            "https://github.com/edithatogo/corpus-cases-medilegal-nz/issues/1#issuecomment-4861258383 "
            "and conductor/tracks/monthly_dynamic_archive_publication_20260701/"
            "phase8_zenodo_draft_evidence.md."
        ),
    ),
    SubIssueSpec(
        marker_id="protected-zenodo-handoff",
        title="Protected Zenodo production handoff",
        summary="Track protected-environment handoff evidence for production DOI publication.",
        status="completed",
        evidence=(
            "Existing evidence: issue #1 comment "
            "https://github.com/edithatogo/corpus-cases-medilegal-nz/issues/1#issuecomment-4861278867 "
            "and conductor/tracks/monthly_dynamic_archive_publication_20260701/"
            "phase8_protected_handoff_evidence.md."
        ),
    ),
    SubIssueSpec(
        marker_id="github-release-assets-attestations",
        title="GitHub release assets and attestations",
        summary="Track GitHub release asset and artifact attestation evidence.",
        status="completed",
        evidence=(
            "Existing evidence: conductor/tracks/github_governance_automation_hardening_20260701/"
            "attestation_verification_evidence.md and issue #1 governance proof comment "
            "https://github.com/edithatogo/corpus-cases-medilegal-nz/issues/1#issuecomment-4861714999."
        ),
    ),
    SubIssueSpec(
        marker_id="public-surface-metadata-evidence",
        title="Public-surface and metadata evidence",
        summary=(
            "Track public-surface audit, metadata package, release evidence, "
            "and discovery surface proof."
        ),
        status="completed",
        evidence=(
            "Existing evidence: release evidence ledgers and "
            "conductor/tracks/monthly_dynamic_archive_publication_20260701/plan.md Phase 8."
        ),
    ),
    SubIssueSpec(
        marker_id="collection-parser-completion",
        title="Collection and parser completion",
        summary="Track non-zero collection, parser fixture, adapter, and processed export proof.",
        status="completed",
        evidence=(
            "Existing evidence: issue #1 comment "
            "https://github.com/edithatogo/corpus-cases-medilegal-nz/issues/1#issuecomment-4861166064 "
            "and conductor/tracks/source_collection_parser_completion_20260701/"
            "collection_proof_evidence.md."
        ),
    ),
    SubIssueSpec(
        marker_id="riopa-project-sync-automation",
        title="RIOPA and project sync automation",
        summary="Track idempotent Conductor/GitHub/RIOPA project sync automation.",
        status="in_progress",
        evidence=f"Current track: conductor/tracks/{SYNC_TRACK_ID}/.",
    ),
]


def parse_markers(body: str) -> dict[str, str]:
    """Parse HTML comment markers from an issue body."""
    return {match.group(1): match.group(2).strip() for match in MARKER_PATTERN.finditer(body)}


def issue_body(spec: SubIssueSpec) -> str:
    """Build a deterministic issue body for a desired sub-issue."""
    return f"""## Summary

{spec.summary}

## Current status

{spec.status}

## Evidence

{spec.evidence}

## Sync metadata

<!-- parent-issue: {PARENT_ISSUE} -->
<!-- riopa-subissue-id: {spec.marker_id} -->
<!-- conductor-track-id: {PARENT_TRACK_ID} -->
"""


def build_issue_index(issues: list[JsonObject]) -> dict[str, JsonObject]:
    """Index existing issues by stable riopa-subissue-id marker."""
    index: dict[str, JsonObject] = {}
    for issue in issues:
        marker_id = parse_markers(str(issue.get("body", ""))).get("riopa-subissue-id")
        if marker_id:
            index[marker_id] = issue
    return index


def detect_duplicate_markers(issues: list[JsonObject]) -> dict[str, list[int]]:
    """Return marker ids that appear on more than one issue."""
    seen: dict[str, list[int]] = {}
    for issue in issues:
        marker_id = parse_markers(str(issue.get("body", ""))).get("riopa-subissue-id")
        if marker_id:
            seen.setdefault(marker_id, []).append(int(issue["number"]))
    return {marker: numbers for marker, numbers in seen.items() if len(numbers) > 1}


def project_item_for_issue(items: list[JsonObject], issue_number: int) -> JsonObject | None:
    """Find a project item for an issue number."""
    for item in items:
        content = item.get("content")
        if isinstance(content, dict) and content.get("number") == issue_number:
            return item
    return None


def status_name_for_spec(spec: SubIssueSpec) -> str:
    """Return GitHub project status display name for a spec."""
    if spec.status == "in_progress":
        return "In Progress"
    return "Done"


def build_sync_plan(
    issues: list[JsonObject],
    riopa_items: list[JsonObject],
    repo_items: list[JsonObject],
) -> JsonObject:
    """Build an idempotent sync plan from issue and project readbacks."""
    issue_index = build_issue_index(issues)
    duplicates = detect_duplicate_markers(issues)
    actions: list[JsonObject] = []
    for spec in SUB_ISSUES:
        issue = issue_index.get(spec.marker_id)
        if issue is None:
            actions.append(
                {
                    "action": "create_issue",
                    "marker_id": spec.marker_id,
                    "title": spec.title,
                    "projects": [RIOPA_PROJECT, REPO_PROJECT],
                }
            )
            continue
        issue_number = int(issue["number"])
        if issue.get("title") != spec.title:
            actions.append(
                {
                    "action": "update_issue_title",
                    "number": issue_number,
                    "expected": spec.title,
                    "actual": issue.get("title"),
                }
            )
        if spec.should_be_closed and issue.get("state") != "CLOSED":
            actions.append({"action": "close_issue", "number": issue_number})
        if not spec.should_be_closed and issue.get("state") != "OPEN":
            actions.append({"action": "reopen_issue", "number": issue_number})
        for project_name, items in ((RIOPA_PROJECT, riopa_items), (REPO_PROJECT, repo_items)):
            item = project_item_for_issue(items, issue_number)
            if item is None:
                actions.append(
                    {
                        "action": "add_to_project",
                        "number": issue_number,
                        "project": project_name,
                        "project_title": project_name,
                    }
                )
                continue
            if item.get("status") != status_name_for_spec(spec):
                actions.append(
                    {
                        "action": "set_status",
                        "number": issue_number,
                        "project": project_name,
                        "project_id": RIOPA_PROJECT_ID
                        if project_name == RIOPA_PROJECT
                        else REPO_PROJECT_ID,
                        "item_id": item["id"],
                        "field_id": RIOPA_STATUS_FIELD_ID
                        if project_name == RIOPA_PROJECT
                        else REPO_STATUS_FIELD_ID,
                        "option_id": spec.status_option_id,
                        "expected": status_name_for_spec(spec),
                        "actual": item.get("status"),
                    }
                )
            if project_name == RIOPA_PROJECT and item.get("mirror source") != "other":
                actions.append(
                    {
                        "action": "set_mirror_source",
                        "number": issue_number,
                        "project": project_name,
                        "project_id": RIOPA_PROJECT_ID,
                        "item_id": item["id"],
                        "field_id": RIOPA_MIRROR_FIELD_ID,
                        "option_id": RIOPA_MIRROR_OTHER_OPTION_ID,
                        "expected": "other",
                        "actual": item.get("mirror source"),
                    }
                )
    return {
        "schema_version": "1.0.0",
        "parent_issue": PARENT_ISSUE,
        "desired_subissue_count": len(SUB_ISSUES),
        "duplicate_markers": duplicates,
        "actions": actions,
        "status": "blocked" if duplicates else ("drift" if actions else "in_sync"),
    }


def run_gh(args: list[str]) -> str:
    """Run a GitHub CLI command and return stdout."""
    completed = subprocess.run(  # noqa: S603
        ["gh", *args],
        check=True,
        stdout=subprocess.PIPE,
        text=True,
        encoding="utf-8",
    )
    return completed.stdout


def load_live_state() -> tuple[list[JsonObject], list[JsonObject], list[JsonObject]]:
    """Load issue and project state from GitHub."""
    issues = json.loads(
        run_gh(
            [
                "issue",
                "list",
                "--state",
                "all",
                "--limit",
                "200",
                "--json",
                "number,title,state,body,url,parent,projectItems",
            ]
        )
    )
    riopa = json.loads(
        run_gh(
            ["project", "item-list", "4", "--owner", OWNER, "--format", "json", "--limit", "200"]
        )
    )["items"]
    repo = json.loads(
        run_gh(
            ["project", "item-list", "7", "--owner", OWNER, "--format", "json", "--limit", "200"]
        )
    )["items"]
    return issues, riopa, repo


def apply_sync_plan(plan: JsonObject) -> None:
    """Apply sync actions that are safe and deterministic."""
    if plan["duplicate_markers"]:
        raise RuntimeError("duplicate riopa-subissue-id markers block apply mode")
    for action in plan["actions"]:
        kind = action["action"]
        if kind == "create_issue":
            spec = next(spec for spec in SUB_ISSUES if spec.marker_id == action["marker_id"])
            run_gh(
                [
                    "issue",
                    "create",
                    "--parent",
                    str(PARENT_ISSUE),
                    "--project",
                    RIOPA_PROJECT,
                    "--project",
                    REPO_PROJECT,
                    "--title",
                    spec.title,
                    "--body",
                    issue_body(spec),
                ]
            )
        elif kind == "close_issue":
            run_gh(
                [
                    "issue",
                    "close",
                    str(action["number"]),
                    "--reason",
                    "completed",
                    "--comment",
                    "Closed by RIOPA project sync after evidence verification.",
                ]
            )
        elif kind == "reopen_issue":
            run_gh(["issue", "reopen", str(action["number"])])
        elif kind in {"set_status", "set_mirror_source"}:
            run_gh(
                [
                    "project",
                    "item-edit",
                    "--project-id",
                    str(action["project_id"]),
                    "--id",
                    str(action["item_id"]),
                    "--field-id",
                    str(action["field_id"]),
                    "--single-select-option-id",
                    str(action["option_id"]),
                ]
            )
        elif kind == "add_to_project":
            run_gh(
                ["issue", "edit", str(action["number"]), "--add-project", action["project_title"]]
            )
        else:
            # Field-level apply needs fresh item ids after possible creation; report it for now.
            raise RuntimeError(f"unsupported apply action requires follow-up readback: {kind}")


def write_json(path: Path, payload: JsonObject) -> None:
    """Write deterministic JSON evidence."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    """Run RIOPA project sync verification or apply mode."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--apply", action="store_true", help="Apply issue create/close/reopen actions."
    )
    parser.add_argument(
        "--output",
        default="generated/project-sync/riopa_project_sync_evidence.json",
        help="Path for JSON sync evidence.",
    )
    args = parser.parse_args(argv)
    issues, riopa_items, repo_items = load_live_state()
    plan = build_sync_plan(issues, riopa_items, repo_items)
    if args.apply and plan["actions"]:
        apply_sync_plan(plan)
        issues, riopa_items, repo_items = load_live_state()
        plan = build_sync_plan(issues, riopa_items, repo_items)
    plan["mode"] = "apply" if args.apply else "dry-run"
    write_json(Path(args.output), plan)
    sys.stdout.write(json.dumps(plan, indent=2, sort_keys=True) + "\n")
    return 1 if plan["status"] == "blocked" else 0


if __name__ == "__main__":
    raise SystemExit(main())
