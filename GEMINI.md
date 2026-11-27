# GEMINI.md — AI & Agent Runtime Configuration

This document specifies the operating parameters, prompt guidelines, and security policies for Gemini and other LLM runtimes integrated into BankingAIPlatform.

## Agent System Boundaries

1. **Role Separation:**
   - System prompts must remain strictly isolated from dynamic user and customer context.
   - User inputs and customer documents must never be concatenated directly into privileged system instructions.
2. **Tool Gateway Interfacing:**
   - Agents never call databases or external systems directly.
   - All tool invocations must route through the BankingAIPlatform Tool Gateway (`/api/v1/tools/execute`).
3. **Strict Structured Output:**
   - All agents producing operational data must validate inputs and outputs against Pydantic v2 schemas.
4. **Prompt Injection & Memory Protection:**
   - All incoming document text and OCR output must be marked as untrusted data envelopes.
   - Memory insertion must verify provenance and reject instruction overriding attempts.
