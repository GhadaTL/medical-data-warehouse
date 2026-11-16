
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
    # Extraire les termes MeSH distincts
    mesh_set = set()

    for value in df["MeSH_Terms"]:

        if pd.isna(value):
            continue

        mesh_list = ast.literal_eval(value)

        if isinstance(mesh_list, list):
            for term in mesh_list:

                mesh_term = str(term).strip()

                if mesh_term:
                    mesh_set.add(mesh_term)

    # Insérer les termes MeSH
    for mesh_term in sorted(mesh_set):

        cursor.execute("""
            INSERT INTO Dim_MeSH (MeSH_Term)
            VALUES (%s)
            ON CONFLICT (MeSH_Term) DO NOTHING;
        """, (mesh_term,))

    connection.commit()

    # Vérifier le nombre total
    cursor.execute("SELECT COUNT(*) FROM Dim_MeSH;")
    count = cursor.fetchone()[0]

    print("Chargement de Dim_MeSH terminé !")
    print("Nombre de termes MeSH distincts :", count)

except Exception as e:
    connection.rollback()
    print("Erreur :", e)

finally:
    cursor.close()
    connection.close()
