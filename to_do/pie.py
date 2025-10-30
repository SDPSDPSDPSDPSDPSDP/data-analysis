# def pie_TO_DO(
#         self, 
#         df: pd.DataFrame, 
#         value: float,
#         label: str, 
#         palette: dict[str, str],
#         output_name: str='pie', 
#         **kwargs
#         ) -> None:
    
#     pie_base(df, value, label, palette, **kwargs)
#     self._export_graph(output_name)

# def pie_binary(self, 
#         input: Dict[bool, int],
#         palette: Dict[bool, str] = {True: Colors.GREEN, False: Colors.RED},
#         output_name: str='pie_binary',
#         **kwargs
#     ) -> None:
#     """Wrapper function for binary pie chart"""

#     df_binary = pd.DataFrame({
#         'key': input.keys(),
#         'value': input.values()
#     })

#     pie_base(df=df_binary, value="value", label="key", palette=palette, label_map=None, **kwargs)
#     self._export_graph(output_name)

# def pie_missing_values(
#     self,
#     df: pd.DataFrame, 
#     col: str,
#     color_missing: str = Colors.RED, 
#     color_non_missing: str = Colors.GREEN, 
#     output_name: str='pie_missing_values',
#     **kwargs
# ) -> None:
#     """Wrapper function for pie chart generation for missing values."""

#     # Count missing and non-missing values
#     missing_count = df[col].isna().sum()
#     non_missing_count = len(df) - missing_count
    
#     # Create a new DataFrame to hold counts
#     df_missing_values = pd.DataFrame({
#         col: ["Missing Values", "Non-Missing Values"],
#         "count": [missing_count, non_missing_count]
#     })
#     palette={"Missing Values": color_missing, "Non-Missing Values": color_non_missing}

#     pie_base(df=df_missing_values, value="count", label=col, palette=palette, label_map=None, **kwargs)
#     self._export_graph(output_name)
