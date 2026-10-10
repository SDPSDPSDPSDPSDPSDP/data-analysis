"""DB2 connection config and pooled engines."""

import functools
import json
import os
import re
from pathlib import Path
from typing import Any, Dict, Union
from sqlalchemy import create_engine, event
from sqlalchemy.engine import URL, Engine

REQUIRED_CONFIG_KEYS = ('user', 'password', 'host', 'port', 'db_name', 'schema')


def load_db_config(
    db_config: Union[Dict[str, str], Path]
) -> Dict[str, str]:
    """Load database configuration from dict or JSON file.
    
    Args:
        db_config: Database configuration dict or Path to JSON config file.
        
    Returns:
        Database configuration dictionary.
        
    Raises:
        ValueError: If db_config format is invalid or file not found.
    """
    if isinstance(db_config, Path):
        if not db_config.exists():
            raise ValueError(
                f"Database config file not found: {db_config}"
            )
        with open(db_config, 'r', encoding='utf-8') as f:
            loaded_config = json.load(f)
        if not isinstance(loaded_config, dict):
            raise ValueError(
                "Database config file must contain a JSON object."
            )
        return loaded_config

    if isinstance(db_config, dict):
        return db_config

    raise ValueError(
        "db_config must be a dictionary or Path object."
    )


def _validate_db_config(db_config: Dict[str, Any]) -> None:
    missing_keys = [key for key in REQUIRED_CONFIG_KEYS if key not in db_config]
    if missing_keys:
        raise KeyError(f"Missing required database config keys: {missing_keys}")
    # SET SCHEMA can't take a bind parameter, so only allow plain identifiers.
    if not re.fullmatch(r'[A-Za-z_][A-Za-z0-9_$#@]*', str(db_config['schema'])):
        raise ValueError(f"Invalid schema name: {db_config['schema']!r}")


@functools.lru_cache(maxsize=None)
def _add_db2_dll_directory() -> None:
    """Windows needs the DB2 client DLLs on the search path; override with DB2_DLL_DIR."""
    dll_dir = os.environ.get("DB2_DLL_DIR", r"C:\Program Files\IBM\SQLLIB\BIN")
    if hasattr(os, "add_dll_directory") and os.path.isdir(dll_dir):
        os.add_dll_directory(dll_dir)


# ponytail: one pooled engine per (connection, schema) for the process lifetime; unbounded,
# fine for a handful of configs. Add eviction/dispose if configs are generated dynamically.
@functools.lru_cache(maxsize=None)
def _get_engine(url: URL, schema: str) -> Engine:
    _add_db2_dll_directory()
    # pool_recycle replaces a pre-ping round trip per query: connections older than 15 min
    # are reopened, which stays under typical DB2/firewall idle timeouts. One connection is
    # kept idle; up to 4 extra for concurrent callers are closed when returned.
    engine = create_engine(url, pool_recycle=900, pool_size=1, max_overflow=4)

    @event.listens_for(engine, "connect")
    def _set_schema(dbapi_connection, _connection_record) -> None:
        # Once per physical connection instead of a round trip per query.
        cursor = dbapi_connection.cursor()
        cursor.execute(f"SET SCHEMA {schema}")
        cursor.close()

    return engine


def get_engine(db_config: Dict[str, Any]) -> Engine:
    """Return the cached DB2 engine for this config (schema set on every new connection)."""
    _validate_db_config(db_config)
    url = URL.create(
        "ibm_db_sa",
        username=db_config['user'],
        password=db_config['password'],
        host=db_config['host'],
        port=int(db_config['port']),
        database=db_config['db_name'],
    )
    return _get_engine(url, str(db_config['schema']))
