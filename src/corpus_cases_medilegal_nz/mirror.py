"""Mirror workflow readiness and evidence helpers."""

from __future__ import annotations

import os
import re
from collections.abc import Mapping
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

JsonObject = dict[str, Any]

MIRROR_WORKFLOW_PATH = Path(".github/workflows/mirror_sync.yml")


def _csv_set(value: str) -> set[str]:
    """Return non-empty comma-separated values as a set."""
    return {item.strip() for item in value.split(",") if item.strip()}


def _workflow_text(root: Path) -> str:
    """Return the mirror workflow text if the file exists."""
    workflow_path = root / MIRROR_WORKFLOW_PATH
    if not workflow_path.is_file():
        return ""
    return workflow_path.read_text(encoding="utf-8")


def mirror_sync_readiness(
    environment: Mapping[str, str] | None = None,
    root: Path = Path(),
) -> JsonObject:
    """Check readiness for the mirror sync workflow."""
    env = environment or os.environ
    root = Path(root)
    workflow_path = root / MIRROR_WORKFLOW_PATH
    workflow_exists = workflow_path.is_file()
    workflow = _workflow_text(root)
    branch_match = bool(
        re.search(r"branches:\s*\[\s*main\s*,\s*master\s*\]", workflow, flags=re.MULTILINE)
        or re.search(r"branches:\s*\n(?:\s*-\s*main\s*\n)?\s*-\s*master\s*", workflow)
    )
    checks: list[JsonObject] = [
        {
            "id": "mirror_workflow_file",
            "status": "ok" if workflow_exists else "missing",
            "secret": False,
            "source": MIRROR_WORKFLOW_PATH.as_posix(),
        },
        {
            "id": "mirror_push_trigger",
            "status": "ok" if "on:" in workflow and "push:" in workflow and branch_match else "missing",
            "secret": False,
            "source": MIRROR_WORKFLOW_PATH.as_posix(),
        },
        {
            "id": "mirror_dispatch_trigger",
            "status": "ok" if "workflow_dispatch:" in workflow else "missing",
            "secret": False,
            "source": MIRROR_WORKFLOW_PATH.as_posix(),
        },
    ]
    credential_checks = (
        ("GIT_MIRROR_URL", ("GIT_MIRROR_URL",)),
        ("GIT_MIRROR_SSH_PRIVATE_KEY", ("GIT_MIRROR_SSH_PRIVATE_KEY",)),
    )
    for name, aliases in credential_checks:
        configured_aliases = [alias for alias in aliases if env.get(alias)]
        checks.append(
            {
                "id": name,
                "status": "configured" if configured_aliases else "gated",
                "secret": True,
                "accepted_names": list(aliases),
                "configured_names": configured_aliases,
            }
        )
    blockers = [check["id"] for check in checks if check["status"] in {"missing", "gated"}]
    return {
        "schema_version": "1.0.0",
        "generated_at": datetime.now(UTC).replace(microsecond=0).isoformat().replace(
            "+00:00", "Z"
        ),
        "status": "ready" if not blockers else "blocked",
        "checks": checks,
        "blockers": blockers,
        "gated_external_writes": [check["id"] for check in checks if check["status"] == "gated"],
        "manual_verification": [
            'gh workflow run "Mirror Sync" --repo edithatogo/corpus-cases-medilegal-nz --ref master',
            'gh run list --repo edithatogo/corpus-cases-medilegal-nz --workflow "Mirror Sync"',
        ],
        "workflow_path": workflow_path.as_posix(),
        "push_trigger_branches": ["main", "master"],
    }
