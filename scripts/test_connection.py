
import os
import psycopg2
from pathlib import Path
from dotenv import load_dotenv

# Chemin vers le dossier principal du projet
BASE_DIR = Path(__file__).resolve().parent.parent

# Charger le fichier .env
load_dotenv(BASE_DIR / ".env")

# Vérifier le chargement des variables
print("Vérification des variables .env :")
print("DB_HOST :", os.getenv("DB_HOST"))
print("DB_NAME :", os.getenv("DB_NAME"))
print("DB_USER :", os.getenv("DB_USER"))
print("DB_PASSWORD chargé :", bool(os.getenv("DB_PASSWORD")))
print("DB_PORT :", os.getenv("DB_PORT"))

# Tester la connexion PostgreSQL
try:
    connection = psycopg2.connect(
        host=os.getenv("DB_HOST"),
        database=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        port=os.getenv("DB_PORT")
    )

    print("\nConnexion à PostgreSQL réussie !")

    cursor = connection.cursor()
    cursor.execute("SELECT current_database();")

    database_name = cursor.fetchone()[0]
    print("Base de données connectée :", database_name)

    cursor.close()
    connection.close()

except Exception as e:
    print("\nErreur de connexion :", e)
