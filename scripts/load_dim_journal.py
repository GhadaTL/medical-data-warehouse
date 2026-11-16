
import os

import pandas as pd
import psycopg2

df = pd.read_csv("data/cleaned/bibliographic_cleaned.csv")

connection = psycopg2.connect(
    host=os.getenv("DB_HOST"),
    database=os.getenv("DB_NAME"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    port=os.getenv("DB_PORT")
)

cursor = connection.cursor()

try:
    # Sélectionner les couples distincts Journal + ISSN
    journals = df[["Journal", "ISSN"]].drop_duplicates()

    for _, row in journals.iterrows():

        journal_name = (
            str(row["Journal"]).strip()
            if pd.notna(row["Journal"]) and str(row["Journal"]).strip()
            else "Unknown"
        )

        issn = (
            str(row["ISSN"]).strip()
            if pd.notna(row["ISSN"]) and str(row["ISSN"]).strip()
            else None
        )

        cursor.execute("""
            SELECT Journal_Key
            FROM Dim_Journal
            WHERE Journal_Name = %s
              AND ISSN IS NOT DISTINCT FROM %s;
        """, (journal_name, issn))

        result = cursor.fetchone()

        if result is None:
            cursor.execute("""
                INSERT INTO Dim_Journal (Journal_Name, ISSN)
                VALUES (%s, %s);
            """, (journal_name, issn))

    connection.commit()

    cursor.execute("SELECT COUNT(*) FROM Dim_Journal;")
    count = cursor.fetchone()[0]

    print("Chargement de Dim_Journal terminé !")
    print("Nombre de revues :", count)

except Exception as e:
    connection.rollback()
    print("Erreur :", e)

finally:
    cursor.close()
    connection.close()
