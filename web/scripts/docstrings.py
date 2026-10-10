# Dumps PlotGraphs docstrings to JSON, keyed by name, for the editor's hover tooltips.
import inspect
import json
import sys

from shirin.plot import PlotGraphs

docs = {"PlotGraphs": inspect.getdoc(PlotGraphs)}
for name, member in inspect.getmembers(PlotGraphs, callable):
    doc = inspect.getdoc(member)
    if not name.startswith("_") and doc:
        docs[name] = doc

with open(sys.argv[1], "w", encoding="utf-8") as f:
    json.dump(docs, f, indent=1)
