## 📊 Dataset Access
The full DuckDB database for this project is available for download:

* [**Download olist_ecommerce.db**](https://github.com/chinwarsoon/dsai-5m-projects/releases/download/Data/olist_ecommerce.db)

### How to load the data in Python:
```python
import duckdb
con = duckdb.connect('olist_ecommerce.db')
print(con.execute("SHOW TABLES").fetchdf())
