# Agent Rules & Behavioral Invariants

1. **Mandatory Pre-Flight Inspection:**
   - Always verify the workspace and environment before proposing code or structural changes.
   - Do not claim a library or system dependency is available without verifying it.

2. **Preserve User Work & Approved Design:**
   - The approved visual designs and UI references are the primary visual design authority.
   - Never replace the approved design with a generic template or boilerplate.

3. **No Unexecuted Claims:**
   - Never report that a test or security check passed unless you invoked the command and captured the output.

4. **Honest Test Discipline:**
   - Tests exist to catch regressions. If an implementation causes a test failure, repair the implementation.
   - Never weaken assertions, delete tests, or comment out checks to simulate success.

5. **Stop Condition Enforcement:**
   - Each phase is bounded. When a phase's tasks are complete, stop and present the phase completion report.
   - Never automatically cascade into subsequent phases without user authorization.

6. **Evidence Preservation:**
   - Every phase completion must link to recorded test logs and scan evidence in `engineering/evidence/`.
