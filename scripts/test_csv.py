
import pandas as pd

# Lire le fichier CSV nettoyé
df = pd.read_csv(
    "data/cleaned/bibliographic_cleaned.csv"
)

# Afficher les premières lignes
print(df.head())

# Afficher les informations du fichier
print("\nNombre de lignes :", len(df))
print("\nColonnes disponibles :")
print(df.columns.tolist())
