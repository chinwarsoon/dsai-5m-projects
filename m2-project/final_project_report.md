# Olist Data Platform Project Report

## 1. Project Briefing
### Problem Statement
The business needed a reliable analytics pipeline to transform raw e-commerce data into decision-ready insights while maintaining data quality and operational repeatability.

### Project Goal
Build an end-to-end data platform that:
1. Ingests and transforms raw operational data.
2. Models data into an analytics-friendly schema.
3. Loads curated data into a warehouse for BI and KPI analysis.
4. Enforces data quality rules.
5. Supports repeatable orchestration and reporting.

### Scope Delivered
1. Data injection and transformation in DuckDB.
2. Star schema design and population (`analytics` schema).
3. ELT pipeline into BigQuery.
4. Data quality checks (Great Expectations + SQL tests).
5. Workflow, architecture, and orchestration documentation.

---

## 2. Project Architecture
### End-to-End Flow
1. Raw CSV files are loaded into DuckDB raw tables.
2. Consolidation is performed through `main_orders_view`.
3. A star schema is built in `analytics` (dimensions + fact).
4. Curated tables are loaded into BigQuery.
5. Data quality checks validate completeness, integrity, and business logic.
6. KPI analysis and charts are generated for reporting.
7. Orchestration enables scheduled ELT + DQ runs.

### Architecture References
- Workflow diagram: [workflow.md](./workflow.md)
- Architecture summary: [architecture.md](./architecture.md)
- Schema visual: [schema_map.png](./schema_map.png)

---

## 3. Insights, Technical Approach, and Design Justification
### 3.1 Key Insights (from project analysis outputs)
1. Revenue and order trends can be tracked monthly for business planning.
2. Category-level performance can guide product focus decisions.
3. Customer segmentation supports targeted lifecycle campaigns.

Associated visual outputs:
- Monthly sales trends: [monthly_sales_trends.png](./monthly_sales_trends.png)
- Customer segmentation: [customer_segmentation_pie_chart.png](./customer_segmentation_pie_chart.png)

### 3.2 Technical Approach
1. **Ingestion and transformation** were handled in DuckDB for local analytical speed and SQL compatibility.
2. **Modeling** used a dimensional approach (`analytics` schema) for BI-friendly queries.
3. **ELT** moved curated tables to BigQuery for scalable cloud analytics.
4. **Data quality** used:
   - Great Expectations for reusable validation contracts.
   - Custom SQL checks for transparent, debuggable rules.
5. **Orchestration design** supports cron, CI/CD (GitHub Actions), or workflow engines (Airflow/Dagster).

### 3.3 Why These Tools Were Chosen
1. **DuckDB**
   - Fast local analytics and easy SQL-based transformation.
   - Simple file-based development for iterative project work.
2. **BigQuery**
   - Managed, scalable warehouse for production-style analytics.
   - Strong fit for downstream KPI querying and reporting.
3. **Great Expectations + SQL checks**
   - GE standardizes rule governance.
   - SQL makes root-cause analysis explicit and fast.
4. **Jupyter notebooks**
   - Supports transparent, auditable, step-by-step development and demonstration.
5. **Flexible orchestration options**
   - Enables migration path from local scheduling to managed orchestration.

### 3.4 Schema Design Justification (Why Star Schema)
Chosen design: dimensional star schema in `analytics`:
1. `fact_orders` as the central transactional fact.
2. `dim_customer`, `dim_product`, `dim_seller`, `dim_geolocation`, `dim_time` as conformed dimensions.

Why this supports efficient querying:
1. **Simpler joins** from one central fact to multiple dimensions.
2. **Faster aggregations** for time-, product-, and customer-oriented KPIs.
3. **Cleaner BI semantics** (measures in facts, attributes in dimensions).
4. **Surrogate keys** improve join consistency and support SCD-ready evolution.
5. **Unknown/default dimension records** preserve referential integrity and minimize dropped facts.

---

## 4. Business Recommendations
### 4.1 Recommendations for Business Executives
1. Prioritize high-performing product categories for promotional budget allocation.
2. Use monthly trend indicators for inventory and campaign timing decisions.
3. Operationalize customer segmentation for retention and upsell programs.
4. Track DQ scorecards as an executive KPI to reduce decision risk from bad data.

### 4.2 Recommendations for Technical Executives
1. Convert notebook-critical steps into scriptized production jobs for reliability.
2. Enforce data quality gates in orchestration (fail pipeline on critical DQ failure).
3. Add metadata logging per run (row counts, failed checks, runtime, lineage stamp).
4. Standardize secrets/config management for environment portability.
5. Move toward managed orchestration (Airflow/Composer/Dagster) as complexity grows.

---

## 5. Risks, Limitations, and Mitigations
### Risks
1. Notebook-first workflows may introduce manual execution drift.
2. External dependency/version changes may affect reproducibility.
3. Data quality gaps can propagate if checks are not gating deployments.
4. Schema changes upstream can break ELT assumptions.

### Mitigations
1. Add scheduled orchestration with explicit task dependencies.
2. Pin package versions and validate environment on startup.
3. Treat critical DQ checks as release blockers.
4. Add schema validation and contract checks before load.

---

## 6. Relevant Files and Artifacts
### Core Notebooks
1. Main workflow notebook: [main.ipynb](./main.ipynb)
2. Data quality plan: [data_quality_test_plan.ipynb](./data_quality_test_plan.ipynb)
3. Great Expectations notebook: [great-expectation.ipynb](./great-expectation.ipynb)
4. Orchestration plan notebook: [pipeline_orchestration_plan.ipynb](./pipeline_orchestration_plan.ipynb)

### Documentation
1. Workflow details and flowchart: [workflow.md](./workflow.md)
2. Architecture document: [architecture.md](./architecture.md)
3. Supporting notes: [notes.md](./notes.md)

### Visuals and Reports
1. Schema map: [schema_map.png](./schema_map.png)
2. Monthly sales chart: [monthly_sales_trends.png](./monthly_sales_trends.png)
3. Customer segmentation chart: [customer_segmentation_pie_chart.png](./customer_segmentation_pie_chart.png)
4. Data quality PDF report: [olist_dq_report.pdf](./olist_dq_report.pdf)

### Data Asset
1. Local warehouse file (not committed): `olist_ecommerce_star.db`

---

## 7. Conclusion
This project delivers a practical analytics foundation with strong architectural structure, a BI-efficient star schema, enforceable data quality controls, and a clear path to production orchestration. The next maturity step is to operationalize scheduling and observability so business teams receive consistent, trusted insights with minimal manual effort.
