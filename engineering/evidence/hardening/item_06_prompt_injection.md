# Item 6 Plan — Prompt-Injection Defenses

## Plan
- Harden `PromptGuard.sanitize_untrusted_envelope` to escape closing envelope/system/instruction tags and add `PromptGuard.build_role_separated_messages` to keep user and document content in `user` role messages separate from `system`.
- Add `backend/tests/fixtures/injections.json` covering "Ignore all previous instructions", fake closing tags, tool-call JSON inside a document, and role-override text.
- Verify Pydantic `ToolExecuteRequest` schema validation and run redteam + chat tests.

## Evidence
```
$ python -m pytest tests/test_ai_chat.py tests/test_ai_redteam_and_safety.py -v
11 passed in 0.73s
```
- **Status:** `VERIFIED`
