
import pandas as pd
import psycopg2
import ast
import os

from pathlib import Path
from dotenv import load_dotenv

# Chemin du projet
BASE_DIR = Path(__file__).resolve().parent.parent

# Charger les variables du fichier .env
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
    # Récupérer tous les auteurs distincts
    authors_set = set()

    for value in df["Authors"]:

        if pd.isna(value):
            continue

        authors_list = ast.literal_eval(value)

        if isinstance(authors_list, list):
            for author in authors_list:

                author_name = str(author).strip()

                if author_name:
                    authors_set.add(author_name)

    # Récupérer les auteurs déjà présents
    cursor.execute("SELECT Author_Name FROM Dim_Author;")

    existing_authors = {
        row[0] for row in cursor.fetchall()
    }

    # Insérer uniquement les nouveaux auteurs
    new_authors = authors_set - existing_authors

    for author_name in sorted(new_authors):

        cursor.execute("""
            INSERT INTO Dim_Author (Author_Name)
            VALUES (%s);
        """, (author_name,))

    connection.commit()

    # Vérifier le nombre total
    cursor.execute("SELECT COUNT(*) FROM Dim_Author;")
    count = cursor.fetchone()[0]

    print("Chargement de Dim_Author terminé !")
    print("Nombre d'auteurs distincts :", count)

except Exception as e:
    connection.rollback()
    print("Erreur :", e)

finally:
    cursor.close()
    connection.close()
