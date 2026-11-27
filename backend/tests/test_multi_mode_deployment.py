import os
import subprocess
import pytest


def _repo_root() -> str:
    return os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_multi_mode_deployment_artifacts_exist() -> None:
    root = _repo_root()
    expected = [
        os.path.join(root, "scripts", "deploy", "Select-Environment.ps1"),
        os.path.join(root, "scripts", "deploy", "Invoke-StagingPreflight.ps1"),
        os.path.join(root, "scripts", "deploy", "Deploy-Staging.ps1"),
        os.path.join(root, "scripts", "deploy", "Deploy-Native.ps1"),
        os.path.join(root, "scripts", "deploy", "Start-Native.ps1"),
        os.path.join(root, "scripts", "deploy", "Stop-Native.ps1"),
        os.path.join(root, "scripts", "deploy", "Test-Native.ps1"),
        os.path.join(root, "scripts", "deploy", "serve_frontend.mjs"),
        os.path.join(root, "buildspec.yml"),
        os.path.join(root, "engineering", "release", "phase_18", "PHASE_18_2_DEPLOYMENT_MODES.md"),
    ]
    for path in expected:
        assert os.path.exists(path), f"Missing multi-mode deployment artifact: {path}"


@pytest.mark.skipif(os.name != "nt", reason="PowerShell script test targets Windows")
def test_native_preflight_succeeds_without_docker() -> None:
    root = _repo_root()
    script = os.path.join(root, "scripts", "deploy", "Invoke-StagingPreflight.ps1")
    result = subprocess.run(
        ["powershell", "-ExecutionPolicy", "Bypass", "-File", script, "-Environment", "WINDOWS_LOCAL", "-Mode", "NATIVE"],
        capture_output=True,
        text=True,
        timeout=20,
    )
    assert result.returncode == 0, f"NATIVE preflight failed: {result.stdout}\n{result.stderr}"
    assert "Active BankingAIPlatform Execution Environment : WINDOWS_LOCAL" in result.stdout
    assert "Active BankingAIPlatform Deployment Mode       : NATIVE" in result.stdout


@pytest.mark.skipif(os.name != "nt", reason="PowerShell script test targets Windows")
def test_environment_and_mode_selection_independent() -> None:
    root = _repo_root()
    script = os.path.join(root, "scripts", "deploy", "Select-Environment.ps1")
    result = subprocess.run(
        ["powershell", "-ExecutionPolicy", "Bypass", "-File", script, "-Environment", "GITHUB_ACTIONS", "-Mode", "AWS_MANAGED"],
        capture_output=True,
        text=True,
        timeout=15,
    )
    assert result.returncode == 0
    assert "GITHUB_ACTIONS" in result.stdout
    assert "AWS_MANAGED" in result.stdout
