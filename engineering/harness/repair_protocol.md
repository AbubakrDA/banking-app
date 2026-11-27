# Repair Protocol

When a test, build, or security check fails during the harness cycle, the following protocol must be strictly observed:

## The 5-Step Repair Sequence

1. **Isolate the Failure:**
   - Read the exact traceback, error message, and failing assertion.
   - Do not guess or apply random edits.

2. **Identify Root Cause:**
   - Determine whether the failure is caused by missing imports, schema mismatch, state violation, or incorrect logic.

3. **Apply Minimal Targeted Fix:**
   - Modify only the code necessary to address the root cause.
   - Maintain backwards compatibility and architectural boundaries.

4. **Prohibition of Test Tampering:**
   - **STRICT RULE:** You must NEVER weaken, delete, comment out, or mock a test just to force it to pass.
   - If the test specification itself had an error, document the exact flaw and justify why the test required correction before touching it.

5. **Regression Verification:**
   - Re-run the failing test until it passes.
   - Re-run all other tests in the module to ensure no collateral regression.
