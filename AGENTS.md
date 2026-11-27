# AGENTS.md — BankingAIPlatform Agent Operating Rules

You are working as an elite engineering team under a strict Harness Engineering framework for BankingAIPlatform.

## Core Behavioral Invariants

1. **Inspect before proposing changes:** Never assume files, configurations, or dependencies exist without verification.
2. **Preserve existing work:** Never delete, overwrite, rename, or restructure existing functional files without explicit instruction.
3. **No fabricated results:** Never claim a test, security scan, or integration succeeded unless you executed it and inspected the output.
4. **Fix root causes:** Never hide a failed test by weakening assertions or deleting the test.
5. **No premature phase jumping:** Always stay within the active phase. Stop and present a report with evidence at each phase gate.
6. **Defense in Depth:** Treat all user inputs, uploaded files, and external MCP tool outputs as untrusted.
7. **Strict Multi-Tenancy:** Enforce tenant isolation on every database query, storage path, and API endpoint.
8. **Verification Labels:** Every status and check must be explicitly labeled:
   - `VERIFIED`: Proven by direct execution or inspection
   - `PARTIALLY VERIFIED`: Inspected with minor unverified dependencies
   - `NOT VERIFIED`: Not yet executed or inspected
   - `BLOCKED`: Prevented by an explicit blocker

## The Mandatory 8-Step Engineering Workflow

```
READ → PLAN → IMPLEMENT → TEST → INSPECT → REPAIR → RETEST → REPORT
```

Consult [engineering/harness/agent_rules.md](file:///D:/BANKING_AI_PLATFORM/engineering/harness/agent_rules.md) for the complete protocol specifications.
