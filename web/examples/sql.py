# %% [setup] Install the sql extra with uv add "shirin[sql]". Put the DB2 credentials in a .env file in your project folder. Variables already set in the environment win over the file.
DB2_USER=me
DB2_PASSWORD=secret
DB2_HOST=db2.example.com
DB2_PORT=50000
DB2_DB_NAME=MYDB
DB2_SCHEMA=MYSCHEMA

# %% [setup] Create the database connection once and reuse it. Arguments left out are read from .env.
from shirin.sql import Database

db = Database()

# %% [setup] Run a query and get a DataFrame. Pass values as params instead of formatting them into the SQL, so DB2 reuses one cached plan.
df = db.sql("SELECT * FROM sales WHERE year = :year", params={"year": 2024})

# %% [setup] Run a .sql file and stream a large result into a Parquet file instead of memory.
from pathlib import Path

db.sql(Path("query.sql"), output_path=Path("results.parquet"))
