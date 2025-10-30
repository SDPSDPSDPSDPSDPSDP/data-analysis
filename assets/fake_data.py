# generate fake datasets

import pandas as pd
import numpy as np
import random
import os

df = pd.DataFrame({
    "label": ["A", "B", "A", "C", "B", "B", "C", "A", "A", "C", "D", "E", "F", "A", "B", "C"],
    "values": [5, 3, 8, 9, 4, 7, 6, 3, 2, 8, 1, 2, 3, 6, 5, 4],
})
df["hue"] = [random.choice(["category_1", "category_2"]) for _ in range(len(df))]
df["label"] = "Label " + df["label"]

# Enlarge the Dataset
original_length = len(df)
multiplier = 10000
df = pd.concat([df] * multiplier, ignore_index=True)

# Ensure more middle values (range: 1-100, higher weights closer to 50)
weights = [100 - abs(50 - x) for x in range(1, 101)]  # Higher weights for middle values
middle_distribution = [random.choices(range(1, 101), weights=weights)[0] for _ in range(len(df))]
df["values"] = middle_distribution

df["hue"] = [random.choice(["category_1", "category_2"]) for _ in range(len(df))]
df['hue2'] = df['hue'] == 'category_1'
# Generate a fake dataset
np.random.seed(42)  # Set a seed for reproducibility

# Create fake data
years = range(2000, 2023)  # Years from 2000 to 2022
cumul_total_docs = np.cumsum(np.random.randint(50, 150, size=len(years)))  # Cumulative document count

# Build the DataFrame
df_documents_by_year = pd.DataFrame({
    'year': years,  # Year values as integers
    'cumul_total_docs': cumul_total_docs  # Cumulative total documents
})

df_documents_by_year