
import os

import pandas as pd
import psycopg2
from psycopg2.extras import execute_values

# 1. Lire le CSV nettoyé
df = pd.read_csv("data/cleaned/bibliographic_cleaned.csv")

# 2. Préparer les données
def clean_text(value):
    if pd.isna(value):
        return None
    return str(value)

def clean_int(value):
    if pd.isna(value):
        return None
    return int(value)

def clean_bool(value):
    if pd.isna(value):
        return None
    return bool(value)

rows = []

for _, row in df.iterrows():
    rows.append((
        clean_text(row["Record_ID"]),
        clean_text(row["Source_File"]),
        clean_text(row["PMID"]),
        clean_text(row["Affiliations"]),
        clean_int(row["Citation_Index"]),
        clean_int(row["Citations_In_XML"]),
        clean_bool(row["Structural_Anomaly"])
    ))

# 3. Connexion à PostgreSQL
connection = psycopg2.connect(
    host=os.getenv("DB_HOST"),
    database=os.getenv("DB_NAME"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    port=os.getenv("DB_PORT")
)

try:
    cursor = connection.cursor()

    # 4. Insérer les données
    query = """
        INSERT INTO staging_article (
            record_id,
            source_file,
            pmid,
            affiliations,
            citation_index,
            citations_in_xml,
            structural_anomaly
        )
        VALUES %s
        ON CONFLICT (record_id) DO NOTHING;
    """

    execute_values(cursor, query, rows)

    connection.commit()

    # 5. Vérifier le nombre de lignes
    cursor.execute("SELECT COUNT(*) FROM staging_article;")
    total = cursor.fetchone()[0]

    print("Chargement terminé !")
    print("Nombre de lignes dans Staging_Article :", total)

except Exception as e:
    connection.rollback()
    print("Erreur pendant le chargement :", e)

finally:
    cursor.close()
    connection.close()
