"""DB2 pooled engines."""

import functools
import os
import re

from sqlalchemy import create_engine, event
from sqlalchemy.engine import URL, Engine


def _validate_schema(schema: str) -> None:
    # SET SCHEMA can't take a bind parameter, so only allow plain identifiers.
    if not re.fullmatch(r'[A-Za-z_][A-Za-z0-9_$#@]*', schema):
        raise ValueError(f"Invalid schema name: {schema!r}")


@functools.lru_cache(maxsize=None)
def _add_db2_dll_directory() -> None:
    """Windows needs the DB2 client DLLs on the search path; override with DB2_DLL_DIR."""
    if not hasattr(os, "add_dll_directory"):
        return
    override = os.environ.get("DB2_DLL_DIR")
    if override is not None and not os.path.isdir(override):
        raise FileNotFoundError(f"DB2_DLL_DIR={override!r} is not a directory")
    dll_dir = override or r"C:\Program Files\IBM\SQLLIB\BIN"
    if os.path.isdir(dll_dir):
        os.add_dll_directory(dll_dir)


# ponytail: one pooled engine per (connection, schema) for the process lifetime; unbounded,
# fine for a handful of configs. Add eviction/dispose if configs are generated dynamically.
@functools.lru_cache(maxsize=None)
def _get_engine(url: URL, schema: str) -> Engine:
    _add_db2_dll_directory()
    # pool_recycle (15 min, under typical DB2/firewall idle timeouts) replaces a pre-ping round trip per query.
    engine = create_engine(url, pool_recycle=900, pool_size=1, max_overflow=4)

    @event.listens_for(engine, "connect")
    def _set_schema(dbapi_connection, _connection_record) -> None:
        # Once per physical connection instead of a round trip per query.
        cursor = dbapi_connection.cursor()
        cursor.execute(f"SET SCHEMA {schema}")
        cursor.close()

    return engine


def get_engine(user: str, password: str, host: str, port: int, db_name: str, schema: str) -> Engine:
    """Return the cached DB2 engine for these credentials (schema set on every new connection)."""
    _validate_schema(schema)
    try:
        port_number = int(port)
    except ValueError:
        raise ValueError(f"DB2 port (DB2_PORT) must be an integer, got {port!r}") from None
    url = URL.create(
        "ibm_db_sa",
        username=user,
        password=password,
        host=host,
        port=port_number,
        database=db_name,
    )
    return _get_engine(url, schema)
