
import pandas as pd

df = pd.read_csv("data/cleaned/bibliographic_cleaned.csv")

columns_to_check = [
    "Authors",
    "Keywords",
    "Affiliations",
    "Language",
    "Publication_Type",
    "MeSH_Terms",
    "Publication_Date"
]

for column in columns_to_check:
    print("\n" + "=" * 50)
    print("COLONNE :", column)
    print("=" * 50)

    for i, value in enumerate(df[column].dropna().head(3)):
        print(f"Exemple {i + 1} :", repr(value))
