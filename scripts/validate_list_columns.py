
import pandas as pd
import ast

df = pd.read_csv("data/cleaned/bibliographic_cleaned.csv")

list_columns = [
    "Authors",
    "Keywords",
    "Affiliations",
    "Language",
    "Publication_Type",
    "MeSH_Terms"
]

for column in list_columns:
    empty_count = 0
    nonempty_count = 0
    invalid_count = 0

    for value in df[column]:
        if pd.isna(value):
            empty_count += 1
            continue

        try:
            parsed = ast.literal_eval(value)

            if isinstance(parsed, list):
                if len(parsed) == 0:
                    empty_count += 1
                else:
                    nonempty_count += 1
            else:
                invalid_count += 1

        except (ValueError, SyntaxError):
            invalid_count += 1

    print(f"\nColonne : {column}")
    print("Listes non vides :", nonempty_count)
    print("Listes vides :", empty_count)
    print("Valeurs invalides :", invalid_count)
    print("Total :", nonempty_count + empty_count + invalid_count)
