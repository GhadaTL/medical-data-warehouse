
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

# Lire le CSV
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
    # Extraire les codes de langue distincts
    languages_set = set()

    for value in df["Language"]:

        if pd.isna(value):
            continue

        languages_list = ast.literal_eval(value)

        if isinstance(languages_list, list):
            for language in languages_list:

                code = str(language).strip().lower()

                if code:
                    languages_set.add(code)

    # Charger les langues
    for code in sorted(languages_set):

        cursor.execute("""
            INSERT INTO Dim_Language
                (Language_Code, Language_Name)
            VALUES (%s, %s)
            ON CONFLICT (Language_Code) DO NOTHING;
        """, (code, None))

    connection.commit()

    # Vérifier le nombre de langues
    cursor.execute("SELECT COUNT(*) FROM Dim_Language;")
    count = cursor.fetchone()[0]

    print("Chargement de Dim_Language terminé !")
    print("Nombre de langues distinctes :", count)

    # Afficher les langues chargées
    cursor.execute("""
        SELECT Language_Code
        FROM Dim_Language
        ORDER BY Language_Code;
    """)

    for row in cursor.fetchall():
        print("-", row[0])

except Exception as e:
    connection.rollback()
    print("Erreur :", e)

finally:
    cursor.close()
    connection.close()
