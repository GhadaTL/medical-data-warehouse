
import pandas as pd
import psycopg2
import ast
import os

from pathlib import Path
from dotenv import load_dotenv

# Chemin du projet
BASE_DIR = Path(__file__).resolve().parent.parent

# Charger les variables .env
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
    # Créer un dictionnaire : PMID -> Article_Key
    cursor.execute("""
        SELECT PMID, Article_Key
        FROM Dim_Article;
    """)
    articles = {
        str(pmid): article_key
        for pmid, article_key in cursor.fetchall()
    }

    # Créer un dictionnaire : Author_Name -> Author_Key
    cursor.execute("""
        SELECT Author_Name, Author_Key
        FROM Dim_Author;
    """)
    authors = {
        name: author_key
        for name, author_key in cursor.fetchall()
    }

    inserted = 0

    # Parcourir les publications
    for _, row in df.iterrows():

        pmid = str(row["PMID"])

        if pmid not in articles:
            continue

        article_key = articles[pmid]

        if pd.isna(row["Authors"]):
            continue

        authors_list = ast.literal_eval(row["Authors"])

        if not isinstance(authors_list, list):
            continue

        for position, author_name in enumerate(authors_list, start=1):

            author_name = str(author_name).strip()

            if author_name not in authors:
                continue

            author_key = authors[author_name]

            cursor.execute("""
                INSERT INTO Bridge_Article_Author
                    (Article_Key, Author_Key, Author_Order)
                VALUES (%s, %s, %s)
                ON CONFLICT (Article_Key, Author_Key) DO NOTHING;
            """, (article_key, author_key, position))

            inserted += cursor.rowcount

    connection.commit()

    cursor.execute("""
        SELECT COUNT(*)
        FROM Bridge_Article_Author;
    """)

    total = cursor.fetchone()[0]

    print("Chargement de Bridge_Article_Author terminé !")
    print("Nouvelles associations insérées :", inserted)
    print("Total des associations :", total)

except Exception as e:
    connection.rollback()
    print("Erreur :", e)

finally:
    cursor.close()
    connection.close()
