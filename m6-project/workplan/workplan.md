# M6 RAG Agent Workplan

## Title and Description
**Title**: M6 Project - RAG-based Document Submittal Register Agent
**Description**: Design and implement a harness agent using classic RAG approach with local components (LangChain, ChromaDB, Ollama/llama3) to query document submission data from CSV with configurable grouping strategies.

## Workplan Document Information
- **Document ID**: WP-M6-001
- **Revision**: 1.9
- **Status**: PHASE 6 COMPLETED - PENDING PHASE 7 APPROVAL
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

## Approval Workflow
**IMPORTANT**: This workplan requires approval before implementation begins. Each phase requires separate approval before execution.

- **Current Status**: PHASE 6 COMPLETED - PENDING PHASE 7 APPROVAL
- **Approval Required For**: Phase 7
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
- [ ] Phase 6 Approved (after Phase 5 completion)
- [ ] Phase 7 Approved (after Phase 6 completion)
- [ ] Phase 8 Approved (after Phase 7 completion)

## Objectives
1. Build a RAG-based agent for querying document submittal register data
2. Implement local infrastructure (no cloud dependencies)
3. Support multiple grouping strategies for testing and optimization
4. Provide web interface for user interaction
5. Ensure compliance with agent_rule.md standards

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
| WP-10 | Ollama/llama3.2:3b integration | RAG Pipeline | Pending | Phase 5 |
| WP-11 | Web interface development | UI | Pending | Phase 6 |
| WP-12 | Grouping strategy testing | Testing | Pending | Phase 7 |
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
- Streamlit (web framework)
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

### Phase 4: Query and Retrieval
**Timeline**: Week 3-4
**Milestones**: Query function implemented, search configured
**Approval Status**: COMPLETED

**What will be updated/created**:
- [x] Create query function in `engine/retriever.py`
- [x] Implement similarity search functionality
- [x] Configure search parameters (k neighbors, score threshold)
- [x] Add filtering capabilities based on metadata
- [x] Implement result ranking and relevance scoring

**Risks and Mitigation**:
- Risk: Poor retrieval quality
  - Mitigation: Test different embedding models, tune parameters
- Risk: Slow query performance
  - Mitigation: Optimize indexing, implement caching

**Potential Issues**:
- Low relevance scores for certain queries
- Inconsistent results across grouping strategies

**Success Criteria**:
- Queries return relevant results
- Search parameters configurable
- Metadata filtering works correctly
- Query performance acceptable

**References**:
- agent_rule.md Section 10 (Function table and call graph)

---

### Phase 5: RAG Pipeline Integration
**Timeline**: Week 4
**Milestones**: Ollama integrated with llama3.2:3b model, RAG chain working
**Approval Status**: COMPLETED

**What will be updated/created**:
- [x] Configure LangChain with Ollama LLM in `engine/llm_integration.py`
- [x] Implement RAG chain (retrieval + generation)
- [x] Design prompt templates for query responses
- [x] Create context assembly from retrieved documents
- [x] Implement response generation with llama3

**Risks and Mitigation**:
- Risk: Ollama connection issues
  - Mitigation: Implement retry logic, fallback mechanisms
- Risk: Poor response quality
  - Mitigation: Iterate on prompt templates, test various prompts

**Potential Issues**:
- LLM hallucination
- Context window limitations
- Slow response generation

**Success Criteria**:
- Ollama connects successfully
- RAG pipeline generates coherent responses
- Prompt templates produce expected output
- End-to-end pipeline works without errors

**References**:
- agent_rule.md Section 5 (Function coding)

---

### Phase 6: Web Interface Development
**Timeline**: Week 5
**Milestones**: Standalone interactive webpage that loads and runs RAG pipeline, serves locally
**Approval Status**: IN PROGRESS

**What will be updated/created**:
- [x] Study HTML design rule and CSS design system requirements
- [x] Create standalone HTML webpage with VS Code layout in `ui/index.html`
- [x] Create Python backend server in `ui/server.py`
- [x] Implement RAG pipeline loading and initialization
- [x] Implement /api/query endpoint
- [x] Add configuration options (grouping strategy, search parameters, k neighbors)
- [ ] Add Flask dependencies to requirements
- [ ] Ensure webpage serves locally without external dependencies
- [ ] Test end-to-end RAG pipeline through web interface

**Risks and Mitigation**:
- Risk: UI complexity
  - Mitigation: Start with simple interface, iterate based on feedback
- Risk: Performance issues
  - Mitigation: Implement async operations, loading indicators

**Potential Issues**:
- Browser compatibility
- Mobile responsiveness
- Accessibility compliance

**Success Criteria**:
- Web interface launches successfully
- User can submit queries
- Results display correctly
- Configuration options work as expected

**References**:
- agent_rule.md Section 11 (UI web design)
- dcc/workplan/ui_design/html_design_rule.md

---

### Phase 7: Testing and Optimization
**Timeline**: Week 6
**Milestones**: All grouping strategies tested, optimal strategy identified

**What will be updated/created**:
- [ ] Create test cases in `test/` folder
- [ ] Run systematic tests with each grouping option
- [ ] Generate test reports in `workplan/reports/` per Section 9
- [ ] Evaluate retrieval quality for each strategy
- [ ] Document performance metrics per grouping strategy
- [ ] Optimize grouping strategy based on results
- [ ] Update `log/issue_log.md` with any issues found
- [ ] Update `log/update_log.md` with test results

**Risks and Mitigation**:
- Risk: Inconsistent test results
  - Mitigation: Use fixed test dataset, run multiple iterations
- Risk: Time constraints
  - Mitigation: Prioritize critical tests, document remaining tests

**Potential Issues**:
- Test data not representative of production
- Performance degradation with large datasets

**Success Criteria**:
- All grouping strategies tested
- Test reports generated per Section 9 format
- Optimal grouping strategy identified
- Performance metrics documented

**References**:
- agent_rule.md Section 9 (Reports for workplans)

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
- CSV data successfully loaded and split
- Records embedded and stored in ChromaDB
- Queries return relevant results
- RAG pipeline generates coherent responses
- Web interface allows user interaction
- Different grouping strategies can be tested and compared
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
