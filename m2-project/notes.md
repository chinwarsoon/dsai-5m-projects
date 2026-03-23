# 1. main.ipynb
The notebook was created in google golab. Please use google colab to open it:
1. Fork this repo to yours.
2. Use Chrome to open your repo, click main.ipynb to open it.
3. Make sure you have Colab extension installed in Chrome. Click the extention to open the notebook.

## 📊 Dataset Access
The full DuckDB database for this project is available for download:

* [**Download olist_ecommerce.db**](https://github.com/chinwarsoon/dsai-5m-projects/releases/download/Data/olist_ecommerce.db)
* [**Dowload olist_ecommerce_star.db**](https://github.com/chinwarsoon/dsai-5m-projects/releases/download/star_schema_data/olist_ecommerce_star.db)


# 2. Pieline
## Olist E-commerce ELT Pipeline (DuckDB to BigQuery)

This project automates the extraction of star-schema data from a local DuckDB instance and loads it into Google BigQuery using **Meltano**. It is designed to work in restricted corporate environments where direct Git access may be limited.

## 📋 Project Overview
This pipeline represents **Step 3** of the Olist data project. It bridges the gap between the local analytical database (DuckDB) and the cloud data warehouse (BigQuery).

* **Source:** `olist.duckdb` (Local)
* **Orchestration:** Meltano
* **Destination:** Google BigQuery (Cloud)

---

## 🚀 Quick Start for Team Members

### 1. Prerequisites
* **Python 3.12**: Required for `tap-duckdb` compatibility. (If using Python 3.13, create a 3.12 environment using Conda).
* **Meltano**: Install via `pip install meltano`.
* **Google Cloud CLI**: Ensure you are authenticated for BigQuery access.

### 2. Environment Setup (`.env`)
Create a file named `.env` in the root directory. Copy and paste the following template into it:

**GOOGLE_APPLICATION_CREDENTIALS**=./auth/service-account-key.json  
**TARGET_BIGQUERY_PROJECT_ID**=your-gcp-project-id  
**TARGET_BIGQUERY_DATASET**=olist_reporting  
**TARGET_BIGQUERY_LOCATION**=US  

---

### 3. Installation
If you have internet/Git access, run:  
`meltano install`

**Note for Restricted Environments:** If `meltano install` fails due to firewall or Git restrictions, you must manually install the DuckDB extractor from the local source folder:

`.\.meltano\extractors\tap-duckdb\venv\Scripts\python.exe -m pip install ./tap-duckdb-main`

---

### 4. Running the Pipeline
To execute the full data sync and move your tables to the cloud, run:

`meltano run tap-duckdb target-bigquery`

---

## 🏗️ Project Structure
* **meltano.yml**: The "Infrastructure as Code" brain of the project.
* **olist.duckdb**: The source database containing the Olist Star Schema.
* **.env**: Local secrets and project-specific variables (Ignored by Git).
* **README.md**: This documentation.

## 📊 Data Flow
1. **Extract**: The `tap-duckdb` connector reads the tables from the local file.
2. **Load**: The `target-bigquery` connector creates the schema and streams data into GCP.

---
*Developed by Frank/Franklin | Data Science & AI Program 2026*
