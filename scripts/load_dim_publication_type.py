
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
    # Extraire les types de publication distincts
    types_set = set()

    for value in df["Publication_Type"]:

        if pd.isna(value):
            continue

        types_list = ast.literal_eval(value)

        if isinstance(types_list, list):
            for publication_type in types_list:

                type_name = str(publication_type).strip()

                if type_name:
                    types_set.add(type_name)

    # Insérer les types
    for type_name in sorted(types_set):

        cursor.execute("""
            INSERT INTO Dim_Publication_Type (Type_Name)
            VALUES (%s)
            ON CONFLICT (Type_Name) DO NOTHING;
        """, (type_name,))

    connection.commit()

    # Vérifier le nombre total
    cursor.execute("SELECT COUNT(*) FROM Dim_Publication_Type;")
    count = cursor.fetchone()[0]

    print("Chargement de Dim_Publication_Type terminé !")
    print("Nombre de types distincts :", count)

except Exception as e:
    connection.rollback()
    print("Erreur :", e)

finally:
    cursor.close()
    connection.close()
