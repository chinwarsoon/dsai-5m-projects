# M6 Project Workplan

## Project Overview
Design a harness agent to implement a classic RAG (Retrieval-Augmented Generation) approach using local components:
- **Framework**: LangChain
- **Vector Database**: ChromaDB (local)
- **LLM**: llama3 via Ollama (local)
- **Data Source**: CSV file with document submission records
- **Interface**: Web-based user interaction

## Data Context
- **File**: `data/processed_dcc_universal.csv`
- **Type**: Document Submittal Register
- **Records**: 13,704 rows
- **Columns**: 47 columns including submission sessions, review status, approval codes, and metadata
- **Chunk Grouping Options** (for testing):
  - `submission_session` - Group records by submission session identifier
  - `document_id` - Group records by document identifier
  - `validation_error` - Group records by validation error types
  - `department` - Group records by department

## Workplan Tasks

### Phase 1: Environment Setup
- [ ] **Task 1**: Set up project environment and dependencies
  - Install LangChain framework
  - Install ChromaDB
  - Configure Ollama integration with llama3 model
  - Set up virtual environment
  - Create requirements.txt with all dependencies
  - **Priority**: HIGH

### Phase 2: Data Processing
- [ ] **Task 2**: Implement CSV loader with row record splitting
  - Load CSV file using LangChain CSV loader
  - Document submittal register data structure understanding
  - Handle data validation and error handling
  - **Priority**: HIGH

- [ ] **Task 3**: Configure chunk grouping options for testing
  - Implement grouping by `submission_session`
  - Implement grouping by `document_id`
  - Implement grouping by `validation_error`
  - Implement grouping by `department`
  - Allow user to select grouping strategy for testing
  - Compare retrieval quality across different grouping strategies
  - Document optimal grouping strategy findings
  - **Priority**: HIGH

### Phase 3: Vector Database Setup
- [ ] **Task 4**: Implement embedding function for row records
  - Select and configure local embedding model
  - Implement embedding generation for CSV row records
  - Test embedding quality and performance
  - **Priority**: HIGH

- [ ] **Task 5**: Set up ChromaDB vector database
  - Initialize ChromaDB instance
  - Create collection/schema for document records
  - Store embedded records with metadata
  - Implement indexing strategy
  - **Priority**: HIGH

### Phase 4: Query and Retrieval
- [ ] **Task 6**: Implement query function
  - Implement similarity search functionality
  - Configure search parameters (k neighbors, score threshold)
  - Add filtering capabilities based on metadata
  - Test query performance and accuracy
  - **Priority**: HIGH

### Phase 5: RAG Pipeline Integration
- [ ] **Task 7**: Integrate Ollama with llama3 model
  - Configure LangChain with Ollama LLM
  - Implement RAG chain (retrieval + generation)
  - Design prompt templates for query responses
  - Test end-to-end RAG pipeline
  - **Priority**: HIGH

### Phase 6: Web Interface
- [ ] **Task 8**: Build web interface
  - Select web framework (e.g., Streamlit, Flask, FastAPI)
  - Design user interface for query input
  - Display search results with relevant context
  - Add configuration options (chunk size, search parameters)
  - **Priority**: MEDIUM

### Phase 7: Testing and Optimization
- [ ] **Task 9**: Test different grouping strategies
  - Run systematic tests with each grouping option (submission_session, document_id, validation_error, department)
  - Evaluate retrieval quality and response accuracy for each strategy
  - Document performance metrics per grouping strategy
  - Optimize grouping strategy based on results
  - **Priority**: MEDIUM

### Phase 8: Documentation
- [ ] **Task 10**: Document setup and usage instructions
  - Create README with installation steps
  - Document configuration options
  - Provide usage examples
  - Add troubleshooting guide
  - **Priority**: LOW

## Dependencies
- Python 3.8+
- LangChain
- ChromaDB
- Ollama (with llama3 model)
- pandas
- sentence-transformers (for embeddings)
- Web framework (TBD)

## Success Criteria
- CSV data successfully loaded and split
- Records embedded and stored in ChromaDB
- Queries return relevant results
- RAG pipeline generates coherent responses
- Web interface allows user interaction
- Different chunk sizes can be tested and compared

## Notes
- All components are local (no cloud dependencies)
- Focus on modularity for easy testing and optimization
- Prioritize functionality over UI polish in initial implementation
