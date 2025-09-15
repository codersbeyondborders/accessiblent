# db.py
import os
from typing import Any, Iterable, List, Optional, Union

import mysql.connector
from mysql.connector import pooling

_pool: Optional[pooling.MySQLConnectionPool] = None


def _conn_config() -> dict:
    """
    Build mysql-connector config for TiDB Cloud.
    TLS is enabled by default. If you have a CA bundle, set TIDB_SSL_CA to its path.
    """
    cfg = {
        "host": os.getenv("TIDB_HOST", "127.0.0.1"),
        "port": int(os.getenv("TIDB_PORT", "4000")),
        "user": os.getenv("TIDB_USER", "root"),
        "password": os.getenv("TIDB_PASSWORD", ""),
        "database": os.getenv("TIDB_DB", "accessibility"),
        "autocommit": True,
        # TiDB Cloud supports TLS. Leave ssl_disabled=False (default). Add ssl_ca if you have it.
        "ssl_disabled": False,
    }
    ssl_ca = os.getenv("TIDB_SSL_CA")
    if ssl_ca:
        cfg["ssl_ca"] = ssl_ca
    return cfg


def init_pool(pool_size: int = None) -> None:
    """
    Initialize a global connection pool. Call this once at app startup.
    """
    global _pool
    if _pool is not None:
        return
    size = int(os.getenv("DB_POOL_SIZE", str(pool_size or 5)))
    cfg = _conn_config()
    _pool = pooling.MySQLConnectionPool(pool_name="tidb_pool", pool_size=size, **cfg)


def _get_conn():
    """
    Get a pooled connection. Requires init_pool() to have been called.
    """
    if _pool is None:
        # Fallback (no pool) — useful in scripts/tests
        return mysql.connector.connect(**_conn_config())
    return _pool.get_connection()


ParamsType = Optional[Union[tuple, dict, List[tuple], List[dict]]]


def q(sql: str, params: ParamsType = None, many: bool = False) -> Any:
    """
    Execute a SQL statement.
    - For SELECT: returns List[dict]
    - For INSERT (single): returns lastrowid (int) if available, else affected row count
    - For UPDATE/DELETE: returns affected row count
    - For executemany (many=True): returns total affected row count

    Notes:
    - TiDB VECTOR columns accept vector literals as JSON strings like '[0.1, 0.2, ...]'.
      If you have a Python list of floats, json.dumps it before passing as a param.
    """
    conn = _get_conn()
    cur = conn.cursor(dictionary=True)
    try:
        if many:
            if not isinstance(params, (list, tuple)):
                raise ValueError("For many=True, params must be a list/tuple of param tuples or dicts.")
            cur.executemany(sql, params)  # autocommit=True
            return cur.rowcount

        cur.execute(sql, params)
        if cur.with_rows:
            rows = cur.fetchall()
            return rows

        # Non-SELECT
        return cur.lastrowid if getattr(cur, "lastrowid", 0) else cur.rowcount
    finally:
        try:
            cur.close()
        finally:
            conn.close()
