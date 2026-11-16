
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
    cursor.execute("""
        SELECT PMID, Article_Key
        FROM Dim_Article;
    """)

    articles = {
        str(pmid): article_key
        for pmid, article_key in cursor.fetchall()
    }

    cursor.execute("""
        SELECT Type_Name, Type_Key
        FROM Dim_Publication_Type;
    """)

    publication_types = {
        name: type_key
        for name, type_key in cursor.fetchall()
    }

    inserted = 0

    for _, row in df.iterrows():

        pmid = str(row["PMID"])

        if pmid not in articles:
            continue

        article_key = articles[pmid]

        if pd.isna(row["Publication_Type"]):
            continue

        type_list = ast.literal_eval(row["Publication_Type"])

        if not isinstance(type_list, list):
            continue

        for type_name in type_list:

            name = str(type_name).strip()

            if name not in publication_types:
                continue

            type_key = publication_types[name]

            cursor.execute("""
                INSERT INTO Bridge_Article_Type
                    (Article_Key, Type_Key)
                VALUES (%s, %s)
                ON CONFLICT (Article_Key, Type_Key) DO NOTHING;
            """, (article_key, type_key))

            inserted += cursor.rowcount

    connection.commit()

    cursor.execute("""
        SELECT COUNT(*)
        FROM Bridge_Article_Type;
    """)

    total = cursor.fetchone()[0]

    print("Chargement de Bridge_Article_Type terminé !")
    print("Nouvelles associations insérées :", inserted)
    print("Total des associations :", total)

except Exception as e:
    connection.rollback()
    print("Erreur :", e)

finally:
    cursor.close()
    connection.close()
