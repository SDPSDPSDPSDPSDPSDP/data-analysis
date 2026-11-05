"""Parquet writer that buffers small fetch chunks into large row groups."""

from pathlib import Path
from typing import List

import pyarrow as pa
import pyarrow.parquet as pq

# Fetch chunks are buffered up to this many rows per row group: one group per 20k-row chunk bloats
# the footer and slows readers, while this still keeps memory bounded.
PARQUET_ROW_GROUP_ROWS = 250_000


class RowGroupWriter:
    """Buffers chunks into row groups of at least PARQUET_ROW_GROUP_ROWS rows."""

    def __init__(self, path: Path, schema: pa.Schema) -> None:
        self._writer = pq.ParquetWriter(path, schema)
        self._pending: List[pa.Table] = []
        self._rows = 0

    def write(self, table: pa.Table) -> None:
        self._pending.append(table.cast(self._writer.schema))
        self._rows += table.num_rows
        if self._rows >= PARQUET_ROW_GROUP_ROWS:
            self.flush()

    def flush(self) -> None:
        if self._pending:
            self._writer.write_table(pa.concat_tables(self._pending))
        self._pending, self._rows = [], 0

    def close(self) -> None:
        self._writer.close()


def drain(writer: RowGroupWriter, spilled: List[Path]) -> None:
    """Copy spilled chunks into writer one at a time, deleting each once read."""
    for path in spilled:
        writer.write(pq.read_table(path))
        path.unlink()
    spilled.clear()
