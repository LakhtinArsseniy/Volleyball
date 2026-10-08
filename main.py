import pandas as pd

df = pd.read_csv(
    "/Users/natalalahtina/Downloads/archive-1/2019-Nov.csv",
    nrows=10000
)

print(df.head())
print(df.columns.tolist())
print(df.info())
print(df.describe())

event_types = df.event_type.value_counts()
print(event_types)

event_percentage = df.event_type.value_counts(normalize=True) * 100
print(event_percentage)

event_summary = pd.DataFrame([event_types, event_percentage])
print(event_summary)