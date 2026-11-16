
import pandas as pd
import psycopg2
import ast
import os

from pathlib import Path
from dotenv import load_dotenv

# Chemin du projet
BASE_DIR = Path(__file__).resolve().parent.parent

# Charger .env
load_dotenv(BASE_DIR / ".env")

# Lire le CSV nettoyé
df = pd.read_csv(
    BASE_DIR / "data" / "cleaned" / "bibliographic_cleaned.csv"
)

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
    # Dictionnaire PMID -> Article_Key
    cursor.execute("""
        SELECT PMID, Article_Key
        FROM Dim_Article;
    """)

    articles = {
        str(pmid): article_key
        for pmid, article_key in cursor.fetchall()
    }

    # Dictionnaire Language_Code -> Language_Key
    cursor.execute("""
        SELECT Language_Code, Language_Key
        FROM Dim_Language;
    """)

    languages = {
        code: language_key
        for code, language_key in cursor.fetchall()
    }

    inserted = 0

    # Parcourir les publications
    for _, row in df.iterrows():

        pmid = str(row["PMID"])

        if pmid not in articles:
            continue

        article_key = articles[pmid]

        if pd.isna(row["Language"]):
            continue

        language_list = ast.literal_eval(row["Language"])

        if not isinstance(language_list, list):
            continue

        for language_code in language_list:

            code = str(language_code).strip().lower()

            if code not in languages:
                continue

            language_key = languages[code]

            cursor.execute("""
                INSERT INTO Bridge_Article_Language
                    (Article_Key, Language_Key)
                VALUES (%s, %s)
                ON CONFLICT (Article_Key, Language_Key) DO NOTHING;
            """, (article_key, language_key))

            inserted += cursor.rowcount

    connection.commit()

    cursor.execute("""
        SELECT COUNT(*)
        FROM Bridge_Article_Language;
    """)

    total = cursor.fetchone()[0]

    print("Chargement de Bridge_Article_Language terminé !")
    print("Nouvelles associations insérées :", inserted)
    print("Total des associations :", total)

except Exception as e:
    connection.rollback()
    print("Erreur :", e)

finally:
    cursor.close()
    connection.close()
