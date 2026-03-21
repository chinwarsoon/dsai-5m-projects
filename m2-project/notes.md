## main.ipynb
The notebook was created in google golab. Please use google colab to open it:
1. Fork this repo to yours.
2. Use Chrome to open your repo, click main.ipynb to open it.
3. Make sure you have Colab extension installed in Chrome. Click the extention to open the notebook.

## 📊 Dataset Access
The full DuckDB database for this project is available for download:

* [**Download olist_ecommerce.db**](https://github.com/chinwarsoon/dsai-5m-projects/releases/download/Data/olist_ecommerce.db)

### How to load the data in Python:
```python
import duckdb
con = duckdb.connect('olist_ecommerce.db')
print(con.execute("SHOW TABLES").fetchdf())
