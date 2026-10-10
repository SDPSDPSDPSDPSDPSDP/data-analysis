"""SQL query execution utilities for IBM DB2 databases."""

from pathlib import Path
from typing import Any, Dict, Optional, Union
import pandas as pd

from . import engine
from .helpers import execute_query, load_sql_query
from .parquet import query_to_parquet


class Database:
    """IBM DB2 connection. Create once, then run queries with ``sql``.

    Args:
        user, password, host, port, db_name: DB2 connection credentials.
        schema: Default schema, set on every new connection. Must be a plain identifier.

    Raises:
        ValueError: If the schema name is not a plain identifier.

    Examples:
        >>> db = Database(user="u", password="p", host="h", port=50000, db_name="d", schema="S1")
        >>> df = db.sql("SELECT * FROM t WHERE year = :year", params={"year": 2024})
        >>> db.sql(Path("query.sql"), output_path=Path("results.parquet"))
    """

    def __init__(self, user: str, password: str, host: str, port: int, db_name: str, schema: str) -> None:
        self._engine = engine.get_engine(user, password, host, port, db_name, schema)

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
