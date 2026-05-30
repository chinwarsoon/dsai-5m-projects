# M6 RAG Agent Workplan

## Title and Description
**Title**: M6 Project - RAG-based Document Submittal Register Agent
**Description**: Design and implement a harness agent using classic RAG approach with local components (LangChain, ChromaDB, Ollama/llama3) to query document submission data from CSV with configurable grouping strategies and structured chunking options for optimized document representation in the vector database.

## Workplan Document Information
- **Document ID**: WP-M6-001
- **Revision**: 3.3
- **Status**: PHASES 1-6 COMPLETED WITH STRUCTURED CHUNKING - ALL REMAINING PENDING ITEMS RESOLVED - READY FOR PHASE 7 APPROVAL
- **Created**: 2026-05-30
- **Version History**:
  - v1.0 (2026-05-30): Initial workplan creation based on agent_rule.md requirements
  - v1.1 (2026-05-30): Updated LLM model to llama3.2:3b, Phase 1 completed
  - v1.2 (2026-05-30): Phase 2 completed - CSV loader and grouping strategies implemented
  - v1.3 (2026-05-30): Phase 3 completed - embedding function and ChromaDB implemented
  - v1.4 (2026-05-30): Phase 4 in progress - query function implementation
  - v1.5 (2026-05-30): Phase 4 completed - query and retrieval implemented
  - v1.6 (2026-05-30): Phase 5 in progress - RAG pipeline integration
  - v1.7 (2026-05-30): Phase 5 completed - Ollama and RAG pipeline integrated
  - v1.8 (2026-05-30): Phase 6 in progress - HTML/CSS/JS webpage with VS Code layout
  - v1.9 (2026-05-30): Phase 6 completed - web interface with Flask backend
  - v2.0 (2026-05-30): Phase 6 pending actions completed - local-only embeddings, Chroma population, and end-to-end Flask/Ollama query verified
  - v3.0 (2026-05-30): Structured Chunking Strategy integrated - added Phase 3.5 with chunking configuration and RAG pipeline selection logic
  - v3.1 (2026-05-30): All phases before Phase 7 completed - automatic CSV→structured chunking selection implemented in RAGPipeline, configuration updated, workplan finalized
  - v3.2 (2026-05-30): Phase 3.5 Extended and Phase 4 NEW items completed - engine/chunking.py created with 3 chunking strategies, CSVLoader chunking support, DocumentStore structured chunk handling, retriever hierarchy awareness and aggregation, fixed assemble_context bug, UI chunking strategy display wired
  - v3.3 (2026-05-30): File upload and async DB rebuild feature - /api/upload endpoint, /api/rebuild with background thread + progress polling, /api/rebuild-status/<task_id> endpoint, progress modal with animated bar and step log in UI

## Approval Workflow
**IMPORTANT**: This workplan requires approval before implementation begins. Each phase requires separate approval before execution.

- **Current Status**: PHASES 1-6 COMPLETED - READY FOR PHASE 7 APPROVAL
- **Approval Required For**: Phase 7 (all prior phases complete)
- **Approval Process**:
  1. Review workplan structure and compliance with agent_rule.md
  2. Review Phase 1 deliverables and timeline
  3. Approve Phase 1 to begin implementation
  4. After Phase 1 completion, review Phase 1 report
  5. Approve Phase 2 before implementation
  6. Continue sequential approval for each phase

**Approval Sign-off**:
- [x] Workplan Structure Approved
- [x] Phase 1 Approved
- [x] Phase 2 Approved (after Phase 1 completion)
- [x] Phase 3 Approved (after Phase 2 completion)
- [x] Phase 4 Approved (after Phase 3 completion)
- [x] Phase 5 Approved (after Phase 4 completion)
- [x] Phase 6 Approved (after Phase 5 completion)
- [x] Phase 3.5 Approved (after Phase 3 completion) - Structured Chunking Strategy
- [x] Phase 3.5 Completed - Automatic CSV→Structured chunking selection implemented
- [x] Phase 3.5 Extended Completed - chunking.py, CSVLoader chunking, DocumentStore structured chunks, UI chunking display
- [x] Phase 4 Completed - retriever hierarchy awareness, chunk aggregation, chunking strategy parameter
- [ ] Phase 7 Approved (after Phase 6 completion)
- [ ] Phase 8 Approved (after Phase 7 completion)

## Objectives
1. Build a RAG-based agent for querying document submittal register data
2. Implement local infrastructure (no cloud dependencies)
3. Support multiple grouping strategies for testing and optimization
4. Implement configurable chunking strategies (row-level, structured, semantic) for optimized document representation
5. Allow RAG pipeline to choose optimal chunking strategy per query or configuration
6. Provide web interface for user interaction
7. Ensure compliance with agent_rule.md standards

## Scope Summary
| ID | Details | Category | Status | Related Phase |
|----|---------|----------|--------|---------------|
| WP-01 | Environment setup with conda environment | Infrastructure | Completed | Phase 1 |
| WP-02 | Project folder structure creation | Infrastructure | Completed | Phase 1 |
| WP-03 | Schema design and implementation | Configuration | Completed | Phase 1 |
| WP-04 | Tiered logging system implementation | Infrastructure | Completed | Phase 1 |
| WP-05 | CSV loader with data column priority processing | Data Processing | Completed | Phase 2 |
| WP-06 | Chunk grouping configuration (4 strategies) | Data Processing | Completed | Phase 2 |
| WP-07 | Embedding function implementation | Vector DB | Completed | Phase 3 |
| WP-08 | ChromaDB setup and storage | Vector DB | Completed | Phase 3 |
| WP-09 | Query function implementation | Retrieval | Completed | Phase 4 |
| WP-10 | Ollama/llama3.2:3b integration | RAG Pipeline | Completed | Phase 5 |
| WP-11 | Web interface development | UI | Completed | Phase 6 |
| WP-11.5 | Structured Chunking Strategy with automatic CSV detection | Data Processing | Completed | Phase 3.5 |
| WP-12 | Grouping strategy testing with chunking variants | Testing | Pending | Phase 7 |
| WP-13 | Documentation creation | Documentation | Pending | Phase 8 |

## Index of Content
1. [Title and Description](#title-and-description)
2. [Workplan Document Information](#workplan-document-information)
3. [Approval Workflow](#approval-workflow)
4. [Objectives](#objectives)
5. [Scope Summary](#scope-summary)
6. [Index of Content](#index-of-content)
7. [Dependencies](#dependencies)
8. [Architecture Alignment](#architecture-alignment)
9. [Implementation Phases](#implementation-phases)
10. [Success Criteria](#success-criteria)
11. [Notes](#notes)
12. [References](#references)
13. [Appendix](#appendix)

## Dependencies

### Software Dependencies
- Python 3.10+
- LangChain
- LangChain Community
- LangChain Core
- ChromaDB
- Ollama (with llama3.2:3b model)
- pandas
- numpy
- sentence-transformers (for embeddings)
- Flask (web framework)
- Flask-CORS
- python-dotenv
- tiktoken

### External Dependencies
- Ollama with llama3.2:3b model installed
- Python 3.10+
- Conda environment manager

### Internal Dependencies
- agent_rule.md compliance
- Schema files in config/ folder
- Data file in data/ folder

### Task Dependencies
- Phase 1 must complete before Phase 2
- Phase 2 must complete before Phase 3
- Phase 3 must complete before Phase 4
- Phase 4 must complete before Phase 5
- Phase 5 must complete before Phase 6

## Architecture Alignment
This workplan aligns with agent_rule.md requirements:
- **Folder Structure**: Complies with Section 6 (archive, config, data, output, test, ui, engine, log, docs, workplan)
- **Data Processing**: Implements Section 1 data column priority rules
- **Schema Design**: Follows Section 2 schema standards (base + setup + config pattern)
- **Module Design**: Adheres to Section 4 module design principles
- **Logging**: Implements Section 6 tiered logging strategy
- **Documentation**: Follows Section 7 documentation requirements
- **Workplan Format**: Complies with Section 8 workplan standards
- **Reporting**: Follows Section 9 report requirements

## Implementation Phases

### Phase 1: Environment and Infrastructure Setup
**Timeline**: Week 1
**Milestones**: Environment ready, folder structure created, schema defined
**Approval Status**: COMPLETED

**What will be updated/created**:
- [x] Create project folder structure (archive, config, data, output, test, ui, engine, log, docs, workplan)
- [x] Update environment.yml with project-specific paths
- [x] Create schema files:
  - `config/m6_base_schema.json` (definitions)
  - `config/m6_setup_schema.json` (properties)
  - `config/m6_config_schema.json` (actual values)
- [x] Implement tiered logging system in `engine/logger.py`
- [x] Create log files:
  - `log/issue_log.md`
  - `log/update_log.md`

**Risks and Mitigation**:
- Risk: Ollama installation issues
  - Mitigation: Document installation steps, provide alternative LLM options
- Risk: Schema complexity
  - Mitigation: Start with simple schema, iterate based on requirements

**Potential Issues**:
- Schema validation errors during implementation
- Logging performance impact on large datasets

**Success Criteria**:
- Conda environment creates successfully
- All folders created per agent_rule.md
- Schema files validate successfully
- Logging system produces tiered output

**References**:
- agent_rule.md Section 2 (Schema), Section 6 (Logging)
- environment.yml

---

### Phase 2: Data Processing
**Timeline**: Week 2
**Milestones**: CSV loader implemented, grouping strategies configured
**Approval Status**: COMPLETED

**What will be updated/created**:
- [x] Create CSV loader in `engine/csv_loader.py`
- [x] Implement data column priority processing per Section 1:
  - Priority 1: Meta data columns (Project_Code, Department, Submission_Session, etc.)
  - Priority 2: Relational keys (Document_ID, Document_Revision, etc.)
  - Priority 3: Derived logic (Submission_Closed, Resubmission_Required, etc.)
- [x] Implement chunk grouping options:
  - Group by `submission_session`
  - Group by `document_id`
  - Group by `validation_error`
  - Group by `department`
- [x] Create configuration file for grouping strategies in `config/grouping_config.json`

**Risks and Mitigation**:
- Risk: Data quality issues in CSV
  - Mitigation: Implement validation checks, log issues per Section 12
- Risk: Memory issues with large dataset
  - Mitigation: Implement chunked processing, monitor memory usage

**Potential Issues**:
- Duplicate columns in data frame
- Forward fill overwriting existing values
- Null handling for different priority columns

**Success Criteria**:
- CSV loads successfully
- Data column priority processing works correctly
- All 4 grouping strategies implemented
- No data loss during processing

**References**:
- agent_rule.md Section 1 (Data columns)
- data/processed_dcc_universal.csv

---

### Phase 3: Vector Database Setup
**Timeline**: Week 3
**Milestones**: Embeddings generated, ChromaDB initialized, records stored
**Approval Status**: COMPLETED

**What will be updated/created**:
- [x] Create embedding function in `engine/embeddings.py`
- [x] Configure local embedding model (sentence-transformers)
- [x] Initialize ChromaDB in `engine/vector_db.py`
- [x] Implement storage of embedded records with metadata
- [x] Create indexing strategy for efficient retrieval

**Risks and Mitigation**:
- Risk: Embedding model performance
  - Mitigation: Test multiple models, select optimal one
- Risk: ChromaDB storage size
  - Mitigation: Implement compression, monitor storage growth

**Potential Issues**:
- Embedding generation timeout on large datasets
- ChromaDB connection issues
- Metadata storage limitations

**Success Criteria**:
- Embeddings generate successfully for all records
- ChromaDB stores records without errors
- Query performance meets requirements (< 1s for simple queries)

**References**:
- agent_rule.md Section 4 (Module design)

---

### Phase 3.5: Structured Chunking Strategy
**Timeline**: Week 3
**Milestones**: Chunking strategies implemented, structured chunking auto-selected for CSV data sources
**Approval Status**: COMPLETED ✅
**Completion Date**: 2026-05-30

**Purpose**: Enable flexible document representation in vector database by supporting multiple chunking strategies. **Automatic strategy selection based on data source ensures optimal performance for structured data (CSV files).**

**What will be updated/created**:
- [x] Add automatic strategy selection logic to RAGPipeline
  - Detects data source type in `config.json` (CSV detected)
  - For CSV data sources: automatically selects **structured chunking** ✅
  - For other sources: uses default strategy (row_level)
  - Configuration: `chunking.auto_select_strategy = true`
- [x] Update `config/m6_config.json` with:
  - New `data_source` section specifying CSV type ✅
  - New `chunking` section with auto-selection settings ✅
  - Structured chunking strategy definition with column groups ✅
- [x] Update `engine/llm_integration.py` RAGPipeline with:
  - `_select_chunking_strategy()` method ✅
  - `get_chunking_strategy()` getter ✅
  - `get_chunking_config()` getter ✅
  - Automatic strategy selection at pipeline initialization ✅
  - Trace logging of strategy selection decisions ✅
- [x] Create chunking strategy module in `engine/chunking.py` (Phase 3.5 Extended)
- [x] Update `engine/csv_loader.py` to support different chunking strategies (Phase 3.5 Extended)
- [x] Update `engine/vector_db.py` DocumentStore to handle structured chunks (Phase 3.5 Extended)
- [x] Update `ui/index.html` to display selected chunking strategy (Phase 3.5 Extended)

**Automatic Strategy Selection Logic**:
```
if data_source.type == "csv":
    selected_strategy = "structured"  # Optimal for tabular data
elif data_source.type == "json":
    selected_strategy = "default" or "semantic"
else:
    selected_strategy = "row_level" (default fallback)
```

**Configuration Structure** (in `m6_config.json`):
```json
{
  "data_source": {
    "type": "csv",
    "path": "path/to/file.csv"
  },
  "chunking": {
    "auto_select_strategy": true,
    "strategy_for_csv": "structured",
    "default_strategy": "row_level",
    "strategies": { ... }
  }
}
```

**Chunking Configuration Details**:
- Store original row index and chunk offset for traceability
- Maintain metadata hierarchy (which columns belong to which chunk)
- Support parent-child relationships between chunks
- Enable filtering by chunk type in vector database queries
- **Structured chunking column groups for CSV data**:
  - Metadata group: Row_Index, Project_Code, Department, Discipline
  - Submission group: Submission_Session, Submission_Date, Submitted_By
  - Documents group: Document_ID, Document_Title, Document_Revision
  - Review status group: Review_Status, Review_Comments, Review_Due_Date
  - Submission status group: Submission_Closed, Resubmission_Required, Validation_Errors

**Risks and Mitigation**:
- Risk: Increased storage requirements with structured chunking
  - Mitigation: Structured chunking only applied when CSV source detected; can disable auto-selection
- Risk: More complex retrieval with hierarchical chunks
  - Mitigation: Implement smart aggregation of results from related chunks
- Risk: Performance impact of chunking logic
  - Mitigation: Profile different strategies, cache chunking results

**Potential Issues**:
- Loss of context when splitting related columns
- Relevance degradation with over-chunking
- Increased metadata complexity

**Success Criteria**:
- Multiple chunking strategies working correctly
- Chunking configuration properly loaded and applied
- **Automatic strategy selection working: CSV sources → structured chunking**
- RAG pipeline successfully uses selected strategy
- Performance acceptable across all strategies
- Traceability maintained (can map chunks back to original rows)
- Data source type correctly detected from config

**Configuration Schema**:
```json
{
  "chunking": {
    "default_strategy": "row_level",
    "auto_select_strategy": true,
    "strategy_for_csv": "structured",
    "strategies": {
      "row_level": {
        "description": "Entire row as single document",
        "enabled": true
      },
      "structured": {
        "description": "Split by column groups",
        "enabled": true,
        "column_groups": [...]
      },
      "semantic": {
        "description": "Split based on semantic boundaries",
        "enabled": false,
        "min_chunk_size": 200,
        "max_chunk_size": 500
      }
    }
  }
}
```

**References**:
- agent_rule.md Section 1 (Data columns)
- agent_rule.md Section 4 (Module design)
- `config/m6_config.json` - Data source configuration

---

### Phase 4: Query and Retrieval
**Timeline**: Week 3-4
**Milestones**: Query function implemented, search configured, works with multiple chunking strategies
**Approval Status**: COMPLETED ✅
**Completion Date**: 2026-05-30
**Integration Updates**:
- Supports structured chunks with hierarchy awareness
- Implements chunk aggregation for related structured chunks
- Compatible with automatic chunking strategy selection from Phase 3.5

**What will be updated/created**:
- [x] Create query function in `engine/retriever.py`
- [x] Implement similarity search functionality
- [x] Configure search parameters (k neighbors, score threshold)
- [x] Add filtering capabilities based on metadata
- [x] Implement result ranking and relevance scoring
- [x] **NEW**: Update retriever to handle structured chunks with hierarchy awareness
- [x] **NEW**: Implement chunk aggregation for related structured chunks
- [x] **NEW**: Add chunking strategy parameter to retrieval pipeline

**Risks and Mitigation**:
- Risk: Poor retrieval quality
  - Mitigation: Test different embedding models, tune parameters, test with different chunking strategies
- Risk: Slow query performance
  - Mitigation: Optimize indexing, implement caching, profile chunking strategies
- Risk: Retrieving orphaned chunks without context
  - Mitigation: Implement parent chunk retrieval when child chunks match

**Potential Issues**:
- Low relevance scores for certain queries across different chunking strategies
- Inconsistent results due to chunk fragmentation
- Performance degradation with structured chunking

**Success Criteria**:
- Queries return relevant results regardless of chunking strategy
- Search parameters configurable and effective
- Metadata filtering works correctly with chunked documents
- Query performance acceptable for all chunking strategies
- Chunk aggregation works correctly for structured chunks

**References**:
- agent_rule.md Section 10 (Function table and call graph)
- Phase 3.5 (Structured Chunking Strategy)

---

### Phase 5: RAG Pipeline Integration
**Timeline**: Week 4
**Milestones**: Ollama integrated with llama3.2:3b model, RAG chain working with automatic chunking strategy selection
**Approval Status**: COMPLETED ✅
**Completion Date**: 2026-05-30
**Integration Updates**:
- Implemented automatic chunking strategy selection in RAGPipeline.__init__()
- Detects CSV data source and automatically selects structured chunking
- Added _select_chunking_strategy() method with intelligent data source detection
- Added get_chunking_strategy() and get_chunking_config() accessors
- Strategy selection happens at pipeline initialization (not runtime)
- All strategy metadata and decisions are logged

**What will be updated/created**:
- [x] Configure LangChain with Ollama LLM in `engine/llm_integration.py`
- [x] Implement RAG chain (retrieval + generation)
- [x] Design prompt templates for query responses
- [x] Create context assembly from retrieved documents
- [x] Implement response generation with llama3
- [x] **NEW**: Add automatic chunking strategy selection to RAG pipeline
  - Detects data source type from config (CSV, JSON, etc.)
  - For CSV: automatically selects structured chunking
  - For other sources: uses default strategy (row_level)
  - Logs strategy selection in trace entries
- [x] **NEW**: Add `_select_chunking_strategy()` method to RAGPipeline
- [x] **NEW**: Add `get_chunking_strategy()` and `get_chunking_config()` getter methods
- [x] **NEW**: Implement chunking strategy parameter propagation through pipeline

**Automatic Strategy Selection at Pipeline Initialization**:
The RAG pipeline will automatically select chunking strategies based on data source:
1. **CSV Data Sources** → **Structured Chunking** (optimal for tabular data)
   - Splits rows into semantic groups (metadata, documents, review status, submission status)
   - Better retrieval for mixed queries
   - Maintains column hierarchy and relationships
2. **Other Sources** → Use configured default strategy (row_level)
3. **Logic Flow**:
   - Config specifies: `data_source.type = "csv"`
   - Config specifies: `chunking.auto_select_strategy = true`
   - Config specifies: `chunking.strategy_for_csv = "structured"`
   - RAGPipeline.__init__ calls `_select_chunking_strategy()`
   - Detects CSV source type
   - Selects "structured" strategy automatically
   - Logs selection: "CSV data source detected - selecting structured chunking strategy"

**Risks and Mitigation**:
- Risk: Ollama connection issues
  - Mitigation: Implement retry logic, fallback mechanisms
- Risk: Poor response quality
  - Mitigation: Iterate on prompt templates, test with different chunking strategies
- Risk: Complexity of automatic strategy selection
  - Mitigation: Start with CSV detection, extend for other data sources iteratively

**Potential Issues**:
- LLM hallucination
- Context window limitations with structured chunks
- Slow response generation with complex strategy switching
- Inconsistent results across different chunking strategies

**Success Criteria**:
- Ollama connects successfully
- RAG pipeline generates coherent responses with any chunking strategy
- Prompt templates produce expected output accounting for chunk context
- End-to-end pipeline works without errors
- **Automatic strategy selection working correctly (CSV → structured)**
- Strategy selection logged in trace entries
- Chunking strategy accessible via `get_chunking_strategy()`
- Configuration accessible via `get_chunking_config()`

**References**:
- agent_rule.md Section 5 (Function coding)
- Phase 3.5 (Structured Chunking Strategy)
- `config/m6_config.json` - Data source and chunking configuration

---

### Phase 6: Web Interface Development
**Timeline**: Week 5
**Milestones**: Standalone interactive webpage that loads and runs RAG pipeline, serves locally, supports chunking strategy selection
**Approval Status**: COMPLETED ✅
**Completion Date**: 2026-05-30
**Integration Updates**:
- Backend server (ui/server.py) fully compatible with automatic chunking strategy selection
- RAG pipeline initialization in server automatically applies CSV→structured strategy
- Frontend ready for chunking strategy display in status bar
- /api/status endpoint can report selected chunking strategy
- /api/query endpoint ready to accept and respect chunking_strategy parameter

**What will be updated/created**:
- [x] Study HTML design rule and CSS design system requirements
- [x] Create standalone HTML webpage with VS Code layout in `ui/index.html`
- [x] Create Python backend server in `ui/server.py`
- [x] Implement RAG pipeline loading and initialization
- [x] Implement /api/query endpoint
- [x] Add configuration options (grouping strategy, search parameters, k neighbors)
- [x] Add Flask dependencies to requirements
- [x] Ensure webpage serves locally without external dependencies
- [x] Test end-to-end RAG pipeline through web interface
- [x] **NEW**: Add chunking strategy selector dropdown to UI
- [x] **NEW**: Update /api/query endpoint to accept chunking_strategy parameter
- [x] **NEW**: Add chunking strategy status to status bar
- [ ] **NEW**: Allow users to compare results from different chunking strategies (deferred to Phase 7)

**Risks and Mitigation**:
- Risk: UI complexity with chunking options
  - Mitigation: Keep UI simple, use collapsible advanced options section
- Risk: Performance issues with strategy switching
  - Mitigation: Implement async operations, loading indicators, cache results

**Potential Issues**:
- Browser compatibility
- Mobile responsiveness
- Accessibility compliance
- UI complexity overwhelming users

**Success Criteria**:
- Web interface launches successfully
- User can submit queries
- Results display correctly
- Chunking strategy selector works as expected
- Users can compare results across strategies if desired
- Configuration options work correctly with chunking strategies

**References**:
- agent_rule.md Section 11 (UI web design)
- dcc/workplan/ui_design/html_design_rule.md
- Phase 3.5 (Structured Chunking Strategy)

---

### Phase 7: Testing and Optimization
**Timeline**: Week 6
**Milestones**: All grouping and chunking strategies tested, optimal combinations identified

**What will be updated/created**:
- [ ] Create test cases in `test/` folder
- [ ] Run systematic tests with each grouping option
- [ ] **NEW**: Run systematic tests with each chunking strategy
- [ ] **NEW**: Test combinations of grouping + chunking strategies
- [ ] Generate test reports in `workplan/reports/` per Section 9
- [ ] Evaluate retrieval quality for each strategy
- [ ] Document performance metrics per grouping strategy
- [ ] **NEW**: Document performance metrics per chunking strategy
- [ ] **NEW**: Document performance metrics per combined strategy pair
- [ ] Optimize grouping and chunking strategies based on results
- [ ] **NEW**: Create strategy selection recommendations
- [ ] Update `log/issue_log.md` with any issues found
- [ ] Update `log/update_log.md` with test results

**Testing Plan**:
1. **Baseline Testing**: Test each strategy in isolation
   - Row-level chunking + each grouping strategy (4 combinations)
   - Structured chunking + each grouping strategy (4 combinations)
   - Semantic chunking + each grouping strategy (4 combinations if enabled)
   
2. **Query Type Testing**: Test different query categories
   - Metadata-focused queries (e.g., "Find all submissions from Department X")
   - Content-focused queries (e.g., "What documents have validation errors?")
   - Mixed queries (e.g., "Show me documents from Department X with errors")
   
3. **Performance Metrics**:
   - Retrieval accuracy (relevance of top-k results)
   - Query latency (time to retrieve and generate response)
   - Storage overhead (database size per strategy)
   - Memory usage during queries
   
4. **Quality Metrics**:
   - Response coherence
   - Answer completeness
   - Source citation accuracy
   - Hallucination rate

**Risks and Mitigation**:
- Risk: Inconsistent test results
  - Mitigation: Use fixed test dataset, run multiple iterations, control randomness
- Risk: Time constraints
  - Mitigation: Prioritize critical tests, document remaining tests for Phase 8
- Risk: Too many strategy combinations
  - Mitigation: Use design of experiments approach to identify key factors

**Potential Issues**:
- Test data not representative of production
- Performance degradation with large datasets
- Inconsistent results across runs
- Chunking overhead could exceed benefits

**Success Criteria**:
- All grouping strategies tested (4 strategies)
- All chunking strategies tested (3+ strategies)
- At least 4 combined strategy pairs evaluated
- Test reports generated per Section 9 format
- Performance metrics documented
- Optimal strategy combination identified
- Strategy selection recommendations documented
- Reproducible test results

**Deliverables**:
- `workplan/reports/phase7_report.md` - Complete test results and analysis
- `test/test_grouping_strategies.py` - Automated grouping strategy tests
- `test/test_chunking_strategies.py` - Automated chunking strategy tests
- `test/test_combined_strategies.py` - Automated tests for strategy combinations
- `test/test_queries.txt` - Standard test query set
- Updated `log/issue_log.md` with findings

**References**:
- agent_rule.md Section 9 (Reports for workplans)
- Phase 3.5 (Structured Chunking Strategy)
- Phase 2 (Grouping strategies)

---

### Phase 8: Documentation
**Timeline**: Week 7
**Milestones**: Complete documentation package
**Approval Status**: PENDING APPROVAL (requires Phase 7 completion and approval)

**What will be updated/created**:
- [ ] Create comprehensive documentation in `docs/` folder per Section 7:
  - Overall summary
  - Content index
  - Key features
  - Documentation map
  - Quick start with mermaid workflow/chart
  - Module/function structure
  - List of functions
  - I/O table
  - Global Parameter Trace Matrix
  - Details of each function/module
  - Debugging and troubleshooting
  - Usage examples
  - Best practice and pending issues
  - Development test results
  - Dependencies and environment
  - Coding and programming engineering standard achieved
- [ ] Create function table and call graph per Section 10
- [ ] Update README with installation and usage instructions

**Risks and Mitigation**:
- Risk: Documentation incomplete
  - Mitigation: Use documentation checklist, review against Section 7
- Risk: Documentation outdated quickly
  - Mitigation: Establish documentation maintenance process

**Potential Issues**:
- Mermaid chart rendering issues
- Function call graph complexity

**Success Criteria**:
- All Section 7 documentation items completed
- Function table and call graph created
- README comprehensive and accurate

**References**:
- agent_rule.md Section 7 (Documentation)
- agent_rule.md Section 10 (Function table and call graph)

---

## Success Criteria
- CSV data successfully loaded with configurable chunking strategies
- Records embedded and stored in ChromaDB with support for structured chunks
- Queries return relevant results with any chunking strategy
- RAG pipeline generates coherent responses and adapts to chunking strategy
- Web interface allows user interaction and chunking strategy selection
- Different grouping strategies can be tested and compared
- Different chunking strategies can be tested and compared
- Optimal chunking strategy combinations identified through testing
- All components are local (no cloud dependencies)
- System complies with agent_rule.md standards

## Notes
- All components are local (no cloud dependencies)
- Focus on modularity for easy testing and optimization
- Prioritize functionality over UI polish in initial implementation
- Each phase requires approval before implementation begins
- Test reports will be generated in workplan/reports/ folder after each phase

## References
- agent_rule.md - Project rules and standards
- readme.md - Project overview
- archive/workplan_v0.1_archived.md - Original workplan (archived)
- archive/workplan_root_v0.1_archived.md - Root workplan (archived)
- environment.yml - Conda environment configuration
- data/processed_dcc_universal.csv - Document submittal register data
- dcc/workplan/ui_design/html_design_rule.md - UI design standards

## Appendix
### Data Column Priority Reference (Section 1)
**Priority 1 - Meta Data Columns**:
- Project_Code, Project_Name, Project_Number
- Department, Discipline, Section_Category
- Submission_Session, Submission_Date
- Constraint: Bounded forward fill

**Priority 2 - Relational Keys & Transactional Data**:
- Document_ID, Document_Number, Document_Title
- Document_Revision, Submission_Session_Revision
- Review_Return_Actual_Date, Review_Due_Date
- Constraint: No aggressive forward fill

**Priority 3 - Derived Logic & Status Flags**:
- Submission_Closed, Resubmission_Required
- Review_Duration, Days_Overdue
- Constraint: Recalculated every pipeline run

### Logging Levels (Section 6)
- Level 0: Silent / errors only
- Level 1: Status/info (milestone progress)
- Level 2: Warning/debug (detailed debugging info)
- Level 3: Trace (deep technical info)
