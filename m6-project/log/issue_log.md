# Issue Log - M6 Project

## Document Information
- **Document ID**: LOG-M6-ISSUE-001
- **Revision**: 1.2
- **Status**: ACTIVE
- **Created**: 2026-05-30
- **Last Updated**: 2026-05-30

## Issue Log Entries

### ID: ISSUE-010
- **Date**: 2026-05-30
- **Severity**: LOW
- **Category**: Phase 6 Verification
- **Description**: Phase 6 end-to-end verification initially exposed local embedding network calls, empty ChromaDB collection, context assembly that dropped oversized retrieved rows, and grouped-query formatting/mapping issues.
- **Status**: RESOLVED
- **Resolution**: Enforced local cached embeddings, populated ChromaDB with 11,851 CSV row documents, wired Chroma to the project embedding adapter, condensed prompt context to include multiple retrieved sources, and fixed grouped-query output for Phase 7 strategy testing.
- **Related Phase**: Phase 6

---

### ID: ISSUE-008
- **Date**: 2026-05-30
- **Severity**: INFO
- **Category**: RAG Pipeline
- **Description**: Phase 5 completed - Ollama and RAG pipeline integrated
- **Status**: RESOLVED
- **Resolution**: All Phase 5 deliverables completed successfully
- **Related Phase**: Phase 5

---

### ID: ISSUE-006
- **Date**: 2026-05-30
- **Severity**: INFO
- **Category**: Vector Database
- **Description**: Phase 3 completed - embedding function and ChromaDB implemented
- **Status**: RESOLVED
- **Resolution**: All Phase 3 deliverables completed successfully
- **Related Phase**: Phase 3

---

### ID: ISSUE-004
- **Date**: 2026-05-30
- **Severity**: HIGH
- **Category**: Environment Setup
- **Description**: Conda environment creation failed during pip dependencies installation (timeout)
- **Status**: RESOLVED
- **Resolution**: Used batch installation approach. Successfully installed pandas, numpy, langchain, chromadb.
- **Related Phase**: Phase 1 (Environment)
- **Impact**: Partially resolved - sentence-transformers still problematic

---

### ID: ISSUE-005
- **Date**: 2026-05-30
- **Severity**: HIGH
- **Category**: Environment Setup
- **Description**: sentence-transformers installation hangs with no response
- **Status**: RESOLVED
- **Resolution**: User manually installed sentence-transformers successfully after activating m6 environment.
- **Related Phase**: Phase 1 (Environment)
- **Impact**: Resolved - local embeddings now available

---

### ID: ISSUE-001
- **Date**: 2026-05-30
- **Severity**: INFO
- **Category**: Setup
- **Description**: Initial project setup - folder structure created per agent_rule.md
- **Status**: RESOLVED
- **Resolution**: Created all required folders (archive, config, data, output, test, ui, engine, log, docs, workplan)
- **Related Phase**: Phase 1

---

### ID: ISSUE-002
- **Date**: 2026-05-30
- **Severity**: LOW
- **Category**: Schema
- **Description**: Minor JSON schema validation warnings in m6_config_schema.json
- **Status**: OPEN
- **Resolution**: Non-critical warnings present, functionality not affected. Can be addressed in future iteration if needed.
- **Related Phase**: Phase 1

---

### ID: ISSUE-011
- **Date**: 2026-05-30
- **Severity**: MEDIUM
- **Category**: Phase 3.5/4 Remaining Actions
- **Description**: Missing chunking strategy module (engine/chunking.py), no structured chunk hierarchy support in retriever, no chunk aggregation, broken `assemble_context` method signature (missing `def` keyword) in llm_integration.py
- **Status**: RESOLVED
- **Resolution**: Created engine/chunking.py with RowLevelChunking, StructuredChunking, SemanticChunking strategies and ChunkingManager; added chunking support to CSVLoader; added structured chunk storage and related chunk retrieval to DocumentStore; implemented chunk aggregation and deduplication in AdvancedRetriever with query_with_chunking(); fixed missing `def` in assemble_context; added chunking_strategy parameter to RAGPipeline.query(); wired chunking strategy display into UI and /api/status endpoint
- **Related Phase**: Phase 3.5, Phase 4

---

## Summary Statistics
- Total Issues: 11
- Resolved: 9
- Open: 2
- Critical: 0
- High: 0
- Medium: 1
- Low: 7
