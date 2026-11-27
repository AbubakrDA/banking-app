# Phase 7 Specification — Knowledge Base & RAG

**Objective:** Implement enterprise-grade Knowledge Base management, semantic chunking, vector embedding generation, pgvector-compatible hybrid retrieval (vector similarity + keyword scoring), reciprocal rank fusion / reranking, RAG poisoning defense, and source citation extraction.

## 1. Scope
- **Knowledge Base Data Architecture (Spec §4D, §13):**
  - `KBCollection`: Multi-tenant collection categorization (e.g. "Policies", "Product Manuals", "Billing & Returns").
  - `KBDocument`: Document tracking with versioning, chunk counts, source type (`file_upload`, `manual_entry`, `faq`, `url`), and indexing status (`draft`, `indexing`, `indexed`, `archived`).
  - `KBChunk`: Chunked text blocks with token counts, sequence index, metadata (headers, section, page), and 384-dimensional dense semantic embedding vectors.
- **Chunking Pipeline:**
  - Configurable chunk size (e.g. 500 characters) with overlap window (e.g. 50 characters).
  - Boundary-aware paragraph and sentence preservation.
- **Deterministic Dense Embeddings:**
  - Standardized embedding generation mapping text tokens into normalized semantic vector spaces.
- **Hybrid Retrieval & Reranking:**
  - Dual-score fusion: `score = alpha * vector_score + (1 - alpha) * keyword_score` (default alpha = 0.7).
  - Cosine vector similarity + lexical BM25 token matching.
  - Top-K ranking with relevance thresholding.
- **RAG Poisoning Defense (Spec §7, GEMINI.md):**
  - Content scanner detecting adversarial prompt injection inside knowledge sources (e.g. prompt override directives, false permission claims).
  - Automatic isolation and security flagging for contaminated knowledge chunks.
- **Source Citation Attachment:**
  - Structured provenance payload (`document_id`, `document_title`, `collection_name`, `chunk_index`, `snippet`).
- **Strict Multi-Tenancy:**
  - Tenant scoping on collections, documents, chunk queries, and vector search. 0% cross-tenant knowledge leakage.

## 2. Acceptance Criteria
- [ ] Collections and documents can be created, updated, and deleted with full tenant isolation.
- [ ] Ingested text is chunked into overlapping segments preserving semantic integrity.
- [ ] Embeddings are generated and scored using vector similarity.
- [ ] Hybrid retrieval combines vector cosine distance with keyword lexical matching.
- [ ] Adversarial prompt injection inside knowledge chunks is detected and neutralized.
- [ ] Retrieved knowledge chunks produce verifiable citation metadata.
- [ ] 100% of automated tests pass without errors.
