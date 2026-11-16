
import pandas as pd
import psycopg2
import ast
import os

from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

df = pd.read_csv(
    BASE_DIR / "data" / "cleaned" / "bibliographic_cleaned.csv"
)

connection = psycopg2.connect(
    host=os.getenv("DB_HOST"),
    database=os.getenv("DB_NAME"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    port=os.getenv("DB_PORT")
)

cursor = connection.cursor()

try:
    # PMID -> Article_Key
    cursor.execute("""
        SELECT PMID, Article_Key
        FROM Dim_Article;
    """)

    articles = {
        str(pmid): article_key
        for pmid, article_key in cursor.fetchall()
    }

    # MeSH_Term -> MeSH_Key
    cursor.execute("""
        SELECT MeSH_Term, MeSH_Key
        FROM Dim_MeSH;
    """)

    mesh_terms = {
        term: mesh_key
        for term, mesh_key in cursor.fetchall()
    }

    inserted = 0

    for _, row in df.iterrows():

        pmid = str(row["PMID"])

        if pmid not in articles:
            continue

        article_key = articles[pmid]

        if pd.isna(row["MeSH_Terms"]):
            continue

        mesh_list = ast.literal_eval(row["MeSH_Terms"])

        if not isinstance(mesh_list, list):
            continue

        for term in mesh_list:

            term_name = str(term).strip()

            if term_name not in mesh_terms:
                continue

            mesh_key = mesh_terms[term_name]

            cursor.execute("""
                INSERT INTO Bridge_Article_MeSH
                    (Article_Key, MeSH_Key)
                VALUES (%s, %s)
                ON CONFLICT (Article_Key, MeSH_Key) DO NOTHING;
            """, (article_key, mesh_key))

            inserted += cursor.rowcount

    connection.commit()

    cursor.execute("""
        SELECT COUNT(*)
        FROM Bridge_Article_MeSH;
    """)

    total = cursor.fetchone()[0]

    print("Chargement de Bridge_Article_MeSH terminé !")
    print("Nouvelles associations insérées :", inserted)
    print("Total des associations :", total)

except Exception as e:
    connection.rollback()
    print("Erreur :", e)

finally:
    cursor.close()
    connection.close()
