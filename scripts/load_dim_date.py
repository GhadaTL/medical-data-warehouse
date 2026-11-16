
import os

import pandas as pd
import psycopg2

# Lire le CSV nettoyé
df = pd.read_csv("data/cleaned/bibliographic_cleaned.csv")

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
    for _, row in df.iterrows():

       # Conversion de l'année
        year = int(row["Year"]) if pd.notna(row["Year"]) else None

        # Conversion du mois
        month_names = {
            "Jan": 1, "Feb": 2, "Mar": 3,
            "Apr": 4, "May": 5, "Jun": 6,
            "Jul": 7, "Aug": 8, "Sep": 9,
            "Oct": 10, "Nov": 11, "Dec": 12
        }

        if pd.notna(row["Month"]):
            month_value = str(row["Month"]).strip()

            if month_value.isdigit():
                month = int(month_value)
            else:
                month = month_names.get(month_value[:3].title())
        else:
            month = None

        # Conversion du jour
        day = int(row["Day"]) if pd.notna(row["Day"]) else None

        # Déterminer la précision de la date
        if day is not None:
            precision = "DAY"
        elif month is not None:
            precision = "MONTH"
        elif year is not None:
            precision = "YEAR"
        else:
            precision = "UNKNOWN"

        original_date = (
            str(row["Publication_Date"])
            if pd.notna(row["Publication_Date"])
            else None
        )

        cursor.execute("""
            SELECT Date_Key
            FROM Dim_Date
            WHERE Year IS NOT DISTINCT FROM %s
              AND Month IS NOT DISTINCT FROM %s
              AND Day IS NOT DISTINCT FROM %s
              AND Date_Precision = %s
              AND Original_Date IS NOT DISTINCT FROM %s;
        """, (year, month, day, precision, original_date))

        result = cursor.fetchone()

        if result is None:
            cursor.execute("""
                INSERT INTO Dim_Date
                (Year, Month, Day, Date_Precision, Original_Date)
                VALUES (%s, %s, %s, %s, %s);
            """, (year, month, day, precision, original_date))

    connection.commit()

    cursor.execute("SELECT COUNT(*) FROM Dim_Date;")
    count = cursor.fetchone()[0]

    print("Chargement de Dim_Date terminé !")
    print("Nombre de dates :", count)

except Exception as e:
    connection.rollback()
    print("Erreur :", e)

finally:
    cursor.close()
    connection.close()
