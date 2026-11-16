
import pandas as pd
import psycopg2
import os
# Lire le fichier CSV nettoyé
df = pd.read_csv("data/cleaned/bibliographic_cleaned.csv")

# Connexion PostgreSQL
connection = psycopg2.connect(
    host=os.getenv("DB_HOST"),
    database=os.getenv("DB_NAME"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    port=os.getenv("DB_PORT")
)

cursor = connection.cursor()

try:
    for _, row in df.iterrows():

        cursor.execute("""
            INSERT INTO Dim_Article (PMID, Title, Abstract, DOI)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (PMID) DO NOTHING;
        """, (
            str(row["PMID"]),
            row["Title"] if pd.notna(row["Title"]) else None,
            row["Abstract"] if pd.notna(row["Abstract"]) else None,
            row["DOI"] if pd.notna(row["DOI"]) else None
        ))

    connection.commit()

    cursor.execute("SELECT COUNT(*) FROM Dim_Article;")
    count = cursor.fetchone()[0]

    print("Chargement de Dim_Article terminé !")
    print("Nombre d'articles :", count)

except Exception as e:
    connection.rollback()
    print("Erreur :", e)

finally:
    cursor.close()
    connection.close()
