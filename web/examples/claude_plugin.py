# %% [setup] Install once in Claude Code. Adds the data-analysis skill, which teaches Claude this package's API.
/plugin marketplace add SDPSDPSDPSDPSDPSDP/data-analysis
/plugin install shirin-charts@shirin-charts

# %% [setup] Ask for a chart as usual. Claude loads the skill on its own when the project uses shirin, or call it directly:
/shirin-charts:data-analysis
