# %% [setup] Install once in Claude Code. Adds the data-analysis skill, which teaches Claude this package's API.
/plugin marketplace add SDPSDPSDPSDPSDPSDP/data-analysis
/plugin install shirin-charts@shirin-charts

# %% [setup] Ask for a chart as usual. Claude loads the skill on its own when the project uses shirin, or call it directly:
/shirin-charts:data-analysis

# %% [skill] What the skill contains. Claude reads the description to decide when to load it, then follows SKILL.md. migration.md is only read when old shirin code turns up.
../shirin-charts/skills/data-analysis

# %% [terminal] What that looks like in Claude Code:
> Make a bar chart of how many fruits are ripe per fruit
* Skill(shirin-charts:data-analysis)
  Successfully loaded skill
* One row per picked fruit, so plot.bar counts the rows. is_ripe goes on hue.
* Write(fruit.py)
  Wrote 7 lines to fruit.py
    from shirin.assets.data import df
    from shirin.plot import Colors, PlotGraphs
    plot = PlotGraphs(
        palette={'is_ripe': {True: Colors.GREEN, False: Colors.RED}},
        label_mapping={'is_ripe': {True: 'Ripe', False: 'Unripe'}}
    )
    plot.bar(df, x='fruit', hue='is_ripe', stacked=True, legend=True, title='Ripe fruit per fruit')
* Here is the chart, stacked so each bar shows its ripe and unripe share:
[chart]
