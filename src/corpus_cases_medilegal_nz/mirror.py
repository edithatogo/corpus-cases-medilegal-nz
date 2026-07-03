"""Mirror workflow readiness and evidence helpers."""

from __future__ import annotations

import os
import re
import subprocess
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


def classify_remote_head(head: str) -> JsonObject:
    """Classify a remote HEAD object id for mirror compatibility."""
    value = head.strip()
    if not value:
        return {"status": "empty", "object_format": "unknown", "compatible": True}
    if re.fullmatch(r"[0-9a-f]{40}", value):
        return {"status": "ok", "object_format": "sha1", "compatible": True}
    if re.fullmatch(r"[0-9a-f]{64}", value):
        return {
            "status": "incompatible",
            "object_format": "sha256",
            "compatible": False,
            "reason": "remote HEAD appears to use SHA-256 object ids; GitHub mirrors are SHA-1.",
        }
    return {
        "status": "unknown",
        "object_format": "unknown",
        "compatible": True,
        "reason": "remote HEAD is not a recognized SHA-1 or SHA-256 object id.",
    }


def _https_readback_url(mirror_url: str) -> str:
    """Return a public HTTPS readback URL for a supported SSH mirror URL."""
    if mirror_url.startswith("git@gitlab.com:"):
        return "https://gitlab.com/" + mirror_url.removeprefix("git@gitlab.com:")
    if mirror_url.startswith("git@codeberg.org:"):
        return "https://codeberg.org/" + mirror_url.removeprefix("git@codeberg.org:")
    return mirror_url


def probe_remote_head(mirror_url: str, *, timeout_seconds: int = 20) -> JsonObject:
    """Probe a remote mirror HEAD using public readback where possible."""
    readback_url = _https_readback_url(mirror_url)
    try:
        completed = subprocess.run(
            ["git", "ls-remote", readback_url, "HEAD"],
            check=False,
            capture_output=True,
            text=True,
            timeout=timeout_seconds,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        return {
            "mirror_url": mirror_url,
            "readback_url": readback_url,
            "status": "probe_failed",
            "object_format": "unknown",
            "compatible": True,
            "reason": str(exc),
        }
    if completed.returncode != 0:
        return {
            "mirror_url": mirror_url,
            "readback_url": readback_url,
            "status": "probe_failed",
            "object_format": "unknown",
            "compatible": True,
            "reason": completed.stderr.strip() or completed.stdout.strip(),
        }
    head = completed.stdout.split()[0] if completed.stdout.split() else ""
    classification = classify_remote_head(head)
    return {
        "mirror_url": mirror_url,
        "readback_url": readback_url,
        "head": head,
        **classification,
    }


def mirror_sync_readiness(
    environment: Mapping[str, str] | None = None,
    root: Path = Path(),
    require_complete_mirror_set: bool = False,
    probe_remotes: bool = False,
    remote_heads: Mapping[str, str] | None = None,
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
            "status": "ok"
            if "on:" in workflow and "push:" in workflow and branch_match
            else "missing",
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
        ("GIT_MIRROR_URL_GITLAB", ("GIT_MIRROR_URL_GITLAB",)),
        ("GIT_MIRROR_URL_CODEBERG", ("GIT_MIRROR_URL_CODEBERG",)),
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
    if require_complete_mirror_set:
        required_target_ids = (
            "GIT_MIRROR_URL",
            "GIT_MIRROR_URL_GITLAB",
            "GIT_MIRROR_URL_CODEBERG",
        )
        configured_targets = [
            check["id"]
            for check in checks
            if check["id"] in required_target_ids and check["status"] == "configured"
        ]
        checks.append(
            {
                "id": "mirror_target_set",
                "status": "configured"
                if set(configured_targets) == set(required_target_ids)
                else "gated",
                "secret": True,
                "accepted_names": list(required_target_ids),
                "configured_names": configured_targets,
            }
        )
    remote_probe_results: list[JsonObject] = []
    remote_head_map = remote_heads or {}
    if probe_remotes or remote_head_map:
        mirror_urls = []
        seen_urls: set[str] = set()
        for name in ("GIT_MIRROR_URL", "GIT_MIRROR_URL_GITLAB", "GIT_MIRROR_URL_CODEBERG"):
            mirror_url = env.get(name, "").strip()
            if mirror_url and mirror_url not in seen_urls:
                seen_urls.add(mirror_url)
                mirror_urls.append(mirror_url)
        for mirror_url in mirror_urls:
            if mirror_url in remote_head_map:
                classification = classify_remote_head(remote_head_map[mirror_url])
                remote_probe_results.append(
                    {
                        "mirror_url": mirror_url,
                        "head": remote_head_map[mirror_url],
                        **classification,
                    }
                )
            elif probe_remotes:
                remote_probe_results.append(probe_remote_head(mirror_url))
        incompatible = [
            result
            for result in remote_probe_results
            if result.get("status") == "incompatible" or result.get("compatible") is False
        ]
        checks.append(
            {
                "id": "remote_object_format",
                "status": "blocked" if incompatible else "ok",
                "secret": False,
                "probe_enabled": probe_remotes,
                "remote_count": len(remote_probe_results),
                "incompatible_count": len(incompatible),
            }
        )
    blockers = [check["id"] for check in checks if check["status"] in {"missing", "gated"}]
    blockers.extend(check["id"] for check in checks if check["status"] == "blocked")
    return {
        "schema_version": "1.0.0",
        "generated_at": datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "status": "ready" if not blockers else "blocked",
        "checks": checks,
        "remote_probe_results": remote_probe_results,
        "blockers": blockers,
        "gated_external_writes": [check["id"] for check in checks if check["status"] == "gated"],
        "manual_verification": [
            'gh workflow run "Mirror Sync" --repo edithatogo/corpus-cases-medilegal-nz --ref master',
            'gh run list --repo edithatogo/corpus-cases-medilegal-nz --workflow "Mirror Sync"',
            "git ls-remote https://gitlab.com/edithatogo/corpus-cases-medilegal-nz.git HEAD",
            "git ls-remote https://codeberg.org/edithatogo/corpus-cases-medilegal-nz.git HEAD",
        ],
        "workflow_path": workflow_path.as_posix(),
        "push_trigger_branches": ["main", "master"],
        "strict_mode": require_complete_mirror_set,
    }
