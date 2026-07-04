import importlib.util
from pathlib import Path

from corpus_cases_medilegal_nz.mirror import classify_remote_head, mirror_sync_readiness

WORKFLOW_PATH = Path(".github/workflows/mirror_sync.yml")
REPORT_SCRIPT_PATH = Path("scripts/build_mirror_probe_report.py")


def _build_markdown_report(report: dict[object, object]) -> str:
    spec = importlib.util.spec_from_file_location("build_mirror_probe_report", REPORT_SCRIPT_PATH)
    assert spec is not None
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module.build_markdown_report(report)


def test_mirror_workflow_skips_when_any_required_secret_is_missing() -> None:
    workflow = WORKFLOW_PATH.read_text(encoding="utf-8")

    assert (
        'for MIRROR_URL in "$GIT_MIRROR_URL" "$GIT_MIRROR_URL_GITLAB" "$GIT_MIRROR_URL_CODEBERG"; do'
        in workflow
    )
    assert "SEEN_MIRROR_URLS[$MIRROR_URL]=1" in workflow
    assert "No mirror URLs are set, skipping mirror." in workflow
    assert 'if [ -z "$GIT_MIRROR_SSH_PRIVATE_KEY" ]; then' in workflow
    assert "GIT_MIRROR_SSH_PRIVATE_KEY is not set, skipping mirror." in workflow


def test_mirror_workflow_quotes_dynamic_shell_values_and_reports_each_target() -> None:
    workflow = WORKFLOW_PATH.read_text(encoding="utf-8")

    assert "git push --force --prune mirror HEAD:${{ github.ref }}" in workflow
    assert "git ls-remote mirror HEAD" in workflow
    assert 'echo "Mirrored $GIT_MIRROR_URL at $MIRROR_HEAD"' in workflow
    assert 'echo "::error::Mirror push failed for $GIT_MIRROR_URL"' in workflow
    assert 'echo "::error::$FAILURES mirror target(s) failed"' in workflow
    assert 'ssh-keyscan -t ed25519 "$HOST"' in workflow
    assert "git remote remove mirror" in workflow


def test_mirror_workflow_has_push_and_manual_dispatch_triggers() -> None:
    workflow = WORKFLOW_PATH.read_text(encoding="utf-8")

    assert "on:" in workflow
    assert "push:" in workflow
    assert "workflow_dispatch:" in workflow
    assert "branches: [ main, master ]" in workflow


def test_mirror_readiness_reports_workflow_and_secret_gating() -> None:
    report = mirror_sync_readiness(
        environment={},
        root=Path(),
    )

    checks = {check["id"]: check for check in report["checks"]}

    assert report["status"] == "blocked"
    assert checks["mirror_workflow_file"]["status"] == "ok"
    assert checks["mirror_push_trigger"]["status"] == "ok"
    assert checks["mirror_dispatch_trigger"]["status"] == "ok"
    assert checks["GIT_MIRROR_URL"]["status"] == "gated"
    assert checks["GIT_MIRROR_URL_GITLAB"]["status"] == "gated"
    assert checks["GIT_MIRROR_URL_CODEBERG"]["status"] == "gated"
    assert checks["GIT_MIRROR_SSH_PRIVATE_KEY"]["status"] == "gated"
    assert "GIT_MIRROR_URL" in report["blockers"]
    assert "GIT_MIRROR_URL_GITLAB" in report["blockers"]
    assert "GIT_MIRROR_URL_CODEBERG" in report["blockers"]
    assert "GIT_MIRROR_SSH_PRIVATE_KEY" in report["blockers"]
    assert report["mirror_target_summary"] == {
        "configured_count": 0,
        "healthy_count": 0,
        "blocked_count": 0,
        "probe_failed_count": 0,
        "providers": [],
    }
    assert report["mirror_targets"][0]["status"] == "gated"


def test_mirror_readiness_strict_requires_all_mirror_targets() -> None:
    report = mirror_sync_readiness(
        environment={
            "GIT_MIRROR_URL": "git@gitlab.com:edithatogo/corpus-cases-medilegal-nz.git",
            "GIT_MIRROR_URL_GITLAB": "git@gitlab.com:edithatogo/corpus-cases-medilegal-nz.git",
            "GIT_MIRROR_URL_CODEBERG": "git@codeberg.org:edithatogo/corpus-cases-medilegal-nz.git",
            "GIT_MIRROR_SSH_PRIVATE_KEY": "key",
        },
        root=Path(),
        require_complete_mirror_set=True,
    )

    checks = {check["id"]: check for check in report["checks"]}

    assert report["status"] == "ready"
    assert report["strict_mode"] is True
    assert checks["mirror_target_set"]["status"] == "configured"


def test_mirror_readiness_strict_blocks_when_any_target_is_missing() -> None:
    report = mirror_sync_readiness(
        environment={
            "GIT_MIRROR_URL": "git@gitlab.com:edithatogo/corpus-cases-medilegal-nz.git",
            "GIT_MIRROR_URL_GITLAB": "git@gitlab.com:edithatogo/corpus-cases-medilegal-nz.git",
            "GIT_MIRROR_SSH_PRIVATE_KEY": "key",
        },
        root=Path(),
        require_complete_mirror_set=True,
    )

    checks = {check["id"]: check for check in report["checks"]}

    assert report["status"] == "blocked"
    assert checks["mirror_target_set"]["status"] == "gated"
    assert "mirror_target_set" in report["blockers"]


def test_remote_head_classification_flags_sha256_as_incompatible() -> None:
    assert classify_remote_head("b70b00f6642634d31299afba8976486328134a2a") == {
        "status": "ok",
        "object_format": "sha1",
        "compatible": True,
    }

    sha256 = "e3dcc84171382b1178636b36a160335af5d35be0fbc8274624bad048299fb50e"
    classification = classify_remote_head(sha256)

    assert classification["status"] == "incompatible"
    assert classification["object_format"] == "sha256"
    assert classification["compatible"] is False


def test_mirror_readiness_probe_blocks_sha256_gitlab_remote() -> None:
    gitlab_url = "git@gitlab.com:edithatogo/corpus-cases-medilegal-nz.git"
    codeberg_url = "git@codeberg.org:edithatogo/corpus-cases-medilegal-nz.git"
    report = mirror_sync_readiness(
        environment={
            "GIT_MIRROR_URL": gitlab_url,
            "GIT_MIRROR_URL_GITLAB": gitlab_url,
            "GIT_MIRROR_URL_CODEBERG": codeberg_url,
            "GIT_MIRROR_SSH_PRIVATE_KEY": "key",
        },
        root=Path(),
        require_complete_mirror_set=True,
        remote_heads={
            gitlab_url: "e3dcc84171382b1178636b36a160335af5d35be0fbc8274624bad048299fb50e",
            codeberg_url: "b70b00f6642634d31299afba8976486328134a2a",
        },
    )

    checks = {check["id"]: check for check in report["checks"]}

    assert report["status"] == "blocked"
    assert checks["remote_object_format"]["status"] == "blocked"
    assert checks["remote_object_format"]["incompatible_count"] == 1
    assert "remote_object_format" in report["blockers"]
    assert report["remote_probe_results"][0]["object_format"] == "sha256"
    assert report["mirror_target_summary"]["configured_count"] == 2
    assert report["mirror_target_summary"]["healthy_count"] == 1
    assert report["mirror_target_summary"]["blocked_count"] == 1
    assert report["mirror_target_summary"]["providers"] == ["codeberg", "gitlab"]
    targets = {target["provider"]: target for target in report["mirror_targets"]}
    assert targets["gitlab"]["status"] == "blocked"
    assert targets["gitlab"]["object_format"] == "sha256"
    assert targets["codeberg"]["status"] == "healthy"
    assert targets["codeberg"]["object_format"] == "sha1"
    assert report["next_actions"] == [
        "Recreate the GitLab mirror as a blank public SHA-1 repository, then rerun mirror-readiness --strict --probe-remotes."
    ]


def test_mirror_readiness_probe_failure_is_reported_not_blocking() -> None:
    codeberg_url = "git@codeberg.org:edithatogo/corpus-cases-medilegal-nz.git"
    report = mirror_sync_readiness(
        environment={
            "GIT_MIRROR_URL_CODEBERG": codeberg_url,
            "GIT_MIRROR_SSH_PRIVATE_KEY": "key",
        },
        root=Path(),
        remote_heads={codeberg_url: "not-a-git-object"},
    )

    assert report["status"] == "blocked"
    assert "remote_object_format" not in report["blockers"]
    assert report["mirror_target_summary"]["configured_count"] == 1
    assert report["mirror_target_summary"]["blocked_count"] == 0
    assert report["mirror_targets"][0]["status"] == "unknown"
    assert report["mirror_targets"][0]["object_format"] == "unknown"


def test_mirror_probe_markdown_report_surfaces_target_health() -> None:
    report = {
        "generated_at": "2026-07-04T00:00:00Z",
        "status": "blocked",
        "blockers": ["remote_object_format"],
        "mirror_target_summary": {
            "configured_count": 2,
            "healthy_count": 1,
            "blocked_count": 1,
            "probe_failed_count": 0,
            "providers": ["codeberg", "gitlab"],
        },
        "mirror_targets": [
            {
                "provider": "gitlab",
                "status": "blocked",
                "object_format": "sha256",
                "head": "e3dcc84171382b1178636b36a160335af5d35be0fbc8274624bad048299fb50e",
                "reason": "remote HEAD appears to use SHA-256 object ids; GitHub mirrors are SHA-1.",
            },
            {
                "provider": "codeberg",
                "status": "healthy",
                "object_format": "sha1",
                "head": "1895a0b7822dc0027393e83cb4c8cfc4a023c63e",
                "reason": "remote HEAD is compatible with GitHub SHA-1 mirroring",
            },
        ],
        "next_actions": [
            "Recreate the GitLab mirror as a blank public SHA-1 repository, then rerun mirror-readiness --strict --probe-remotes."
        ],
    }

    markdown = _build_markdown_report(report)

    assert "- Status: `blocked`" in markdown
    assert "- Blockers: `remote_object_format`" in markdown
    assert "| gitlab | blocked | sha256 |" in markdown
    assert "| codeberg | healthy | sha1 |" in markdown
    assert "Recreate the GitLab mirror" in markdown
