
import pandas as pd
import psycopg2
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

# Fonctions de nettoyage
def clean_text(value):
    if pd.isna(value):
        return None
    value = str(value).strip()
    return value if value else None


def clean_number(value):
    if pd.isna(value):
        return None

    month_names = {
        "Jan": 1, "Feb": 2, "Mar": 3, "Apr": 4,
        "May": 5, "Jun": 6, "Jul": 7, "Aug": 8,
        "Sep": 9, "Oct": 10, "Nov": 11, "Dec": 12
    }

    value = str(value).strip()

    if value in month_names:
        return month_names[value]

    return int(float(value))


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
    # 1. Récupérer les clés des articles
    cursor.execute("""
        SELECT PMID, Article_Key
        FROM Dim_Article;
    """)

    articles = {
        str(pmid): article_key
        for pmid, article_key in cursor.fetchall()
    }

    # 2. Récupérer les clés des dates
    cursor.execute("""
        SELECT Date_Key, Year, Month, Day
        FROM Dim_Date;
    """)

    dates = {}

    for date_key, year, month, day in cursor.fetchall():
        signature = (
            clean_number(year),
            clean_number(month),
            clean_number(day)
        )
        dates[signature] = date_key

    # 3. Récupérer les clés des journaux
    cursor.execute("""
        SELECT Journal_Key, Journal_Name, ISSN
        FROM Dim_Journal;
    """)

    journals = {}

    for journal_key, journal_name, issn in cursor.fetchall():
        signature = (
            clean_text(journal_name),
            clean_text(issn)
        )
        journals[signature] = journal_key

    inserted = 0
    missing_dates = 0
    missing_journals = 0

    # 4. Parcourir les articles
    for _, row in df.iterrows():

        pmid = str(row["PMID"])

        if pmid not in articles:
            continue

        article_key = articles[pmid]

        # Date de publication
        date_signature = (
            clean_number(row["Year"]),
            clean_number(row["Month"]),
            clean_number(row["Day"])
        )

        date_key = dates.get(date_signature)

        if date_key is None:
            missing_dates += 1

        # Journal
        journal_name = clean_text(row["Journal"])
        issn = clean_text(row["ISSN"])

        # Le chargement de Dim_Journal utilise Unknown
        if journal_name is None:
            journal_name = "Unknown"

        journal_key = journals.get((journal_name, issn))

        if journal_key is None:
            missing_journals += 1

        # Nombre d'auteurs
        authors_count = clean_number(row["Authors_Count"])

        if authors_count is None:
            authors_count = 0

        # Présence du résumé
        abstract = clean_text(row["Abstract"])
        has_abstract = abstract is not None

        # Présence du DOI
        doi = clean_text(row["DOI"])
        has_doi = doi is not None

        # Insertion dans Fact_Article
        cursor.execute("""
            INSERT INTO Fact_Article (
                Article_Key,
                Date_Key,
                Journal_Key,
                Authors_Count,
                Has_Abstract,
                Has_DOI,
                Publication_Count
            )
            VALUES (%s, %s, %s, %s, %s, %s, 1)
            ON CONFLICT (Article_Key) DO NOTHING;
        """, (
            article_key,
            date_key,
            journal_key,
            authors_count,
            has_abstract,
            has_doi
        ))

        inserted += cursor.rowcount

    connection.commit()

    # 5. Vérifier le nombre total de lignes
    cursor.execute("""
        SELECT COUNT(*)
        FROM Fact_Article;
    """)

    total = cursor.fetchone()[0]

    print("Chargement de Fact_Article terminé !")
    print("Nouvelles lignes insérées :", inserted)
    print("Total des lignes :", total)
    print("Articles sans date correspondante :", missing_dates)
    print("Articles sans journal correspondant :", missing_journals)

except Exception as e:
    connection.rollback()
    print("Erreur :", e)

finally:
    cursor.close()
    connection.close()
