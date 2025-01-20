import pyodbc
import os
from dotenv import load_dotenv  # Importation de load_dotenv

# Charger les variables d'environnement depuis le fichier .env
load_dotenv()

# Paramètres de connexion (bug pour user non resolu: nous n'utiliserons pas .env)
server = os.getenv('SERVER') 
database = os.getenv('DB') 

username='jvcb'
pwd='cbjv592023!'

# Vérification des variables d'environnement
if not all([server, database, username, pwd]):
    raise ValueError("Une ou plusieurs variables d'environnement sont manquantes")

# String de connexion
#conn_str = f'DRIVER={{ODBC Driver 18 for SQL Server}};SERVER={server};PORT=1433;DATABASE={database};UID={username};PWD={pwd}'

conn_str = ("Driver={ODBC Driver 18 for SQL Server};"
            "Server=tcp:adventureworks-server-hdf.database.windows.net,1433;"
            "Database=adventureworks;"
            "Uid=jvcb;"
            "Pwd=cbjv592023!;"
            "Encrypt=yes;"
            "TrustServerCertificate=no;"
            "Connection Timeout=30;")
try:
    # Etablissement de la connexion
    conn = pyodbc.connect(conn_str, trusted_connection='no')
    print("*****Connexion réussie à la base de données.")

    # Créer un curseur pour exécuter des requêtes SQL
    cursor = conn.cursor()

#     # requête SQL (lister les tables)
#     cursor.execute("SELECT name FROM sys.tables")
#     tables = cursor.fetchall()

#     # Affichage des tables
#     for table in tables:
#         print(table[0])
    

#     # Fermeture de la connexion et du curseur
#     cursor.close()
#     conn.close()
#     print("Connexion fermée.")
# except Exception as e:
#     print("Erreur de connexion:", e)

    # Lister les tables disponibles
    print("\nTables disponibles dans la base de données :")
    cursor.execute("SELECT name FROM sys.tables")
    tables = cursor.fetchall()
    for table in tables:
        print(f"- {table[0]}")

    # Lister les colonnes de la table 'product'
    print("\nColonnes de la table 'product' :")
    cursor.execute("""
        SELECT COLUMN_NAME 
        FROM INFORMATION_SCHEMA.COLUMNS 
        WHERE TABLE_NAME = 'product'
    """)
    columns = cursor.fetchall()
    for column in columns:
        print(f"- {column[0]}")

    # Fermeture du curseur et de la connexion
    cursor.close()
    conn.close()
    print("\nConnexion fermée.")

except Exception as e:
    print("Erreur de connexion :", e)