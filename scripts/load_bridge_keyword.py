
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

    # Dictionnaire Keyword_Name -> Keyword_Key
    cursor.execute("""
        SELECT Keyword_Name, Keyword_Key
        FROM Dim_Keyword;
    """)

    keywords = {
        name: keyword_key
        for name, keyword_key in cursor.fetchall()
    }

    inserted = 0

    # Parcourir les publications
    for _, row in df.iterrows():

        pmid = str(row["PMID"])

        if pmid not in articles:
            continue

        article_key = articles[pmid]

        if pd.isna(row["Keywords"]):
            continue

        keyword_list = ast.literal_eval(row["Keywords"])

        if not isinstance(keyword_list, list):
            continue

        for keyword in keyword_list:

            keyword_name = str(keyword).strip()

            if keyword_name not in keywords:
                continue

            keyword_key = keywords[keyword_name]

            cursor.execute("""
                INSERT INTO Bridge_Article_Keyword
                    (Article_Key, Keyword_Key)
                VALUES (%s, %s)
                ON CONFLICT (Article_Key, Keyword_Key) DO NOTHING;
            """, (article_key, keyword_key))

            inserted += cursor.rowcount

    connection.commit()

    cursor.execute("""
        SELECT COUNT(*)
        FROM Bridge_Article_Keyword;
    """)

    total = cursor.fetchone()[0]

    print("Chargement de Bridge_Article_Keyword terminé !")
    print("Nouvelles associations insérées :", inserted)
    print("Total des associations :", total)

except Exception as e:
    connection.rollback()
    print("Erreur :", e)

finally:
    cursor.close()
    connection.close()
