from pathlib import Path

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
