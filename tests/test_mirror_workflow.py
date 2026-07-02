from pathlib import Path

from corpus_cases_medilegal_nz.mirror import mirror_sync_readiness

WORKFLOW_PATH = Path(".github/workflows/mirror_sync.yml")


def test_mirror_workflow_skips_when_any_required_secret_is_missing() -> None:
    workflow = WORKFLOW_PATH.read_text(encoding="utf-8")

    assert 'for MIRROR_URL in "$GIT_MIRROR_URL" "$GIT_MIRROR_URL_GITLAB" "$GIT_MIRROR_URL_CODEBERG"; do' in workflow
    assert "No mirror URLs are set, skipping mirror." in workflow
    assert 'if [ -z "$GIT_MIRROR_SSH_PRIVATE_KEY" ]; then' in workflow
    assert "GIT_MIRROR_SSH_PRIVATE_KEY is not set, skipping mirror." in workflow


def test_mirror_workflow_quotes_dynamic_shell_values() -> None:
    workflow = WORKFLOW_PATH.read_text(encoding="utf-8")

    assert 'echo "$GIT_MIRROR_URL"' in workflow
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
