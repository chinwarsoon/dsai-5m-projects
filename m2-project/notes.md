## 📊 Dataset Access
The full DuckDB database for this project is available for download:

* [**Download olist_ecommerce.db**](https://github.com/YourUsername/YourRepo/releases/download/v1.0.0/olist_ecommerce.db)

### How to load the data in Python:
```python
import duckdb
con = duckdb.connect('olist_ecommerce.db')
print(con.execute("SHOW TABLES").fetchdf())
