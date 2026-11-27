# Evidence Requirements

Every completed phase and task must record undeniable evidence of successful execution.

## Required Artifacts per Phase

1. **Execution Logs:**
   - Raw CLI output of test runners (`pytest`, `vitest`, `playwright`).
   - Timestamps and exit codes.
   - Stored in `engineering/evidence/phase_{XX}/logs/`.

2. **Security Scan Outputs:**
   - Output from static analysis tools (`semgrep`, `bandit`, `gitleaks`).
   - Recorded zero-vulnerability or approved exception status.
   - Stored in `engineering/evidence/phase_{XX}/security/`.

3. **Code Change Manifest:**
   - List of all files created or modified.
   - Git commit hash corresponding to the phase baseline.

4. **Phase Completion Report:**
   - Placed at root (`PHASE_{XX}_COMPLETION_REPORT.md`) and archived in `engineering/evidence/phase_{XX}/`.
   - Explicitly stating acceptance criteria status and verification labels.
