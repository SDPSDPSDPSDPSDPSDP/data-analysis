"""SQL query execution utilities for IBM DB2 databases."""

import os
from pathlib import Path
from typing import Any, Dict, Optional, Union
import pandas as pd
from dotenv import find_dotenv, load_dotenv

from . import engine
from .helpers import execute_query, load_sql_query
from .parquet import query_to_parquet


class Database:
    """IBM DB2 connection. Create once, then run queries with ``sql``.

    Each argument left out is read from an environment variable (``DB2_USER``,
    ``DB2_PASSWORD``, ``DB2_HOST``, ``DB2_PORT``, ``DB2_DB_NAME``, ``DB2_SCHEMA``).
    A ``.env`` file in the working directory (or a parent) is loaded first; variables
    already set in the environment win over the file.

    Args:
        user, password, host, port, db_name: DB2 connection credentials.
        schema: Default schema, set on every new connection. Must be a plain identifier.

    Raises:
        ValueError: If an argument is missing from both the call and the environment,
                    or the schema name is not a plain identifier.

    Examples:
        >>> db = Database()  # everything from .env
        >>> db = Database(user="u", password="p", host="h", port=50000, db_name="d", schema="S1")
        >>> df = db.sql("SELECT * FROM t WHERE year = :year", params={"year": 2024})
        >>> db.sql(Path("query.sql"), output_path=Path("results.parquet"))
    """

    def __init__(
        self,
        user: Optional[str] = None,
        password: Optional[str] = None,
        host: Optional[str] = None,
        port: Optional[int] = None,
        db_name: Optional[str] = None,
        schema: Optional[str] = None,
    ) -> None:
        load_dotenv(find_dotenv(usecwd=True))
        given = {'user': user, 'password': password, 'host': host, 'port': port, 'db_name': db_name, 'schema': schema}
        credentials = {name: value if value is not None else os.environ.get(f'DB2_{name.upper()}')
                       for name, value in given.items()}
        missing = [f'DB2_{name.upper()}' for name, value in credentials.items() if value is None]
        if missing:
            raise ValueError(f"Missing database credentials: pass them to Database() or set {missing} in .env")
        self._engine = engine.get_engine(**credentials)

    def sql(
        self,
        query: Union[str, Path],
        params: Optional[Dict[str, Any]] = None,
        output_path: Optional[Path] = None,
    ) -> Optional[pd.DataFrame]:
        """Run a query.

        Args:
            query: SQL string or Path to a .sql file.
            params: Optional bind parameters for ``:name`` placeholders, e.g. ``{"year": 2024}``.
                    Prefer this over formatting values into SQL: DB2 reuses one cached plan
                    instead of compiling every literal value. With params the query is parsed
                    by SQLAlchemy, so a literal colon followed by a word (e.g. ``'12:00'``)
                    must be escaped as ``'12\\:00'``.
            output_path: Optional Path to stream results into a Parquet file (fetched in chunks).

        Returns:
            DataFrame, or None when output_path is given.

        Raises:
            ValueError: If query is not a string or Path, or the file does not exist.
        """
        query_string = load_sql_query(query)
        if output_path:
            query_to_parquet(query_string, self._engine, output_path, params=params)
            return None
        return execute_query(query_string, self._engine, params=params)
