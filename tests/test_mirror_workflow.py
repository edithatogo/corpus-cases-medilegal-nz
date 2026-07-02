from pathlib import Path

from corpus_cases_medilegal_nz.mirror import mirror_sync_readiness

WORKFLOW_PATH = Path(".github/workflows/mirror_sync.yml")


def test_mirror_workflow_skips_when_any_required_secret_is_missing() -> None:
    workflow = WORKFLOW_PATH.read_text(encoding="utf-8")

    assert 'if [ -z "$GIT_MIRROR_URL" ]; then' in workflow
    assert "GIT_MIRROR_URL is not set, skipping mirror." in workflow
    assert 'if [ -z "$GIT_MIRROR_SSH_PRIVATE_KEY" ]; then' in workflow
    assert "GIT_MIRROR_SSH_PRIVATE_KEY is not set, skipping mirror." in workflow


def test_mirror_workflow_quotes_dynamic_shell_values() -> None:
    workflow = WORKFLOW_PATH.read_text(encoding="utf-8")

    assert 'echo "$GIT_MIRROR_URL"' in workflow
    assert 'ssh-keyscan -t ed25519 "$HOST"' in workflow


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
    assert checks["GIT_MIRROR_SSH_PRIVATE_KEY"]["status"] == "gated"
    assert "GIT_MIRROR_URL" in report["blockers"]
    assert "GIT_MIRROR_SSH_PRIVATE_KEY" in report["blockers"]
