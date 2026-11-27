# Harness Engineering System

BankingAIPlatform is engineered using a deterministic, evidence-driven harness.

## Directory Structure

- `agent_rules.md`: Mandatory behavioral invariants for agents and engineers.
- `task_protocol.md`: Task definition template and execution lifecycle.
- `verification_protocol.md`: Automated and manual testing requirements.
- `repair_protocol.md`: Root-cause resolution rules (forbids weakening or hiding tests).
- `security_guardrails.md`: DevSecOps and runtime security constraints.
- `evidence_requirements.md`: Standards for test logs, scan outputs, and completion reports.

## The Engineering Loop

```
1. READ     -> Inspect requirements, existing codebase, and boundaries.
2. PLAN     -> Define exact scope, acceptance criteria, and expected files.
3. IMPLEMENT-> Write clean, modular, typed code adhering to specifications.
4. TEST     -> Run unit, integration, and security checks.
5. INSPECT  -> Verify test and scan outputs against acceptance criteria.
6. REPAIR   -> If tests fail, diagnose and fix the implementation. Never alter tests to pass falsely.
7. RETEST   -> Rerun full test suite to guarantee regression freedom.
8. REPORT   -> Produce a verifiable completion report with evidence.
```
