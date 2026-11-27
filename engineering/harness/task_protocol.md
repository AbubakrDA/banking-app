# Task Protocol

Every task undertaken must follow this structured specification:

## Task Specification Template

```markdown
### Task ID: [PHASE]-[MODULE]-[TASK_NUMBER]
**Title:** [Concise Imperative Title]
**Module:** [Module A-J or Cross-Cutting]
**Phase:** [Phase 0 to 16]

#### 1. Scope
- **Included:** [Explicit list of features/components to implement]
- **Excluded:** [Out-of-scope items deferred to later tasks]

#### 2. Acceptance Criteria
- [ ] AC-1: [Measurable, verifiable criterion]
- [ ] AC-2: [Measurable, verifiable criterion]

#### 3. Expected Files & Components
- `path/to/file1.ext` (Create/Modify)
- `path/to/file2.ext` (Create/Modify)

#### 4. Security & Safety Controls
- [Input validation, authorization checks, threat mitigations]

#### 5. Verification Commands
```bash
# Exact commands required to verify completion
```

#### 6. Verification Status
- Status: [VERIFIED / PARTIALLY VERIFIED / NOT VERIFIED / BLOCKED]
- Evidence reference: `engineering/evidence/phase_XX/...`
```
