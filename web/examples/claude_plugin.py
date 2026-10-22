# %% [setup] Install once in Claude Code. Adds the data-analysis skill, which teaches Claude this package's API.
/plugin marketplace add SDPSDPSDPSDPSDPSDP/data-analysis
/plugin install shirin-charts@shirin-charts

# %% [setup] Ask for a chart as usual. Claude loads the skill on its own when the project uses shirin, or call it directly:
/shirin-charts:data-analysis

# %% [skill] What the skill contains. Claude reads the description to decide when to load it, then follows SKILL.md. migration.md is only read when old shirin code turns up.
../shirin-charts/skills/data-analysis

# %% [terminal] What that looks like in Claude Code:
> Make a bar chart of how many fruits are ripe per fruit in data/fruit.csv
* Skill(shirin-charts:data-analysis)
  Successfully loaded skill
* Read(data/fruit.csv)
  Read 120 lines
* One row per picked fruit, so plot.bar counts the rows. is_ripe goes on hue.
* Write(fruit.py)
  Wrote 5 lines to fruit.py
    import pandas as pd
    from shirin.plot import PlotGraphs
    df = pd.read_csv('data/fruit.csv')
    plot = PlotGraphs()
    plot.bar(df, x='fruit', hue='is_ripe', title='Ripe fruit per fruit')
* Created fruit.py. Run it in your notebook to see the chart inline.
