An MCP for this package could expose things like:

List available plot types — so Claude Code knows what charts exist without having to grep the codebase
Get options/schema for a plot type — return the full BarPlotOptions, LinePlotOptions etc. fields so Claude knows exactly what parameters are valid

The main tradeoff: Claude Code can already read your source files directly and does a decent job understanding the package from code. The MCP would make it faster and more reliable — instead of Claude having to infer the API from reading several files, it gets a clean structured answer. The value grows as the package grows.