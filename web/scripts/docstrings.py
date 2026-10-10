# Dumps PlotGraphs and tool docstrings to JSON, keyed by name, for the editor's hover tooltips.
import inspect
import json
import sys

from shirin.number_format import format_compact, format_percentage, format_thousands
from shirin.plot import PlotGraphs
from shirin.sql import Database

docs = {"PlotGraphs": inspect.getdoc(PlotGraphs)}
for name, member in inspect.getmembers(PlotGraphs, callable):
    doc = inspect.getdoc(member)
    if not name.startswith("_") and doc:
        docs[name] = doc
for member in (format_thousands, format_percentage, format_compact, Database, Database.sql):
    docs[member.__name__] = inspect.getdoc(member)

with open(sys.argv[1], "w", encoding="utf-8") as f:
    json.dump(docs, f, indent=1)
