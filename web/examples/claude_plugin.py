# %% [setup] Install once in Claude Code. Adds the shirin skill, which teaches Claude this package's API.
/plugin marketplace add SDPSDPSDPSDPSDPSDP/data-analysis
/plugin install shirin-charts@shirin-charts

# %% [setup] Ask for a chart as usual. Claude loads the skill on its own when the project uses shirin, or call it directly:
/shirin-charts:shirin bar chart of sales per region

# %% [setup] Get skill updates.
/plugin marketplace update shirin-charts
