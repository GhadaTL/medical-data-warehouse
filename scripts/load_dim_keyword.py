
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
    # Extraire les mots-clés distincts
    keywords_set = set()

    for value in df["Keywords"]:

        if pd.isna(value):
            continue

        keywords_list = ast.literal_eval(value)

        if isinstance(keywords_list, list):
            for keyword in keywords_list:

                keyword_name = str(keyword).strip()

                if keyword_name:
                    keywords_set.add(keyword_name)

    # Insérer les mots-clés
    for keyword_name in sorted(keywords_set):

        cursor.execute("""
            INSERT INTO Dim_Keyword (Keyword_Name)
            VALUES (%s)
            ON CONFLICT (Keyword_Name) DO NOTHING;
        """, (keyword_name,))

    connection.commit()

    # Vérifier le nombre total
    cursor.execute("SELECT COUNT(*) FROM Dim_Keyword;")
    count = cursor.fetchone()[0]

    print("Chargement de Dim_Keyword terminé !")
    print("Nombre de mots-clés distincts :", count)

except Exception as e:
    connection.rollback()
    print("Erreur :", e)

finally:
    cursor.close()
    connection.close()
