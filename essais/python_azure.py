import os
from dotenv import load_dotenv
import pyodbc

load_dotenv()

# Variables d'environnement à récupérer
server = os.getenv('AZURE_SQL_SERVER')
database = os.getenv('AZURE_SQL_DATABASE')
username = os.getenv('AZURE_SQL_USERNAME')
password = os.getenv('AZURE_SQL_PASSWORD')


#connection_string = os.getenv("AZURE_SQL_CONNECTIONSTRING")
connection_string = f'Driver={{ODBC Driver 18 for SQL Server}};Server=tcp:{server},1433;Database={database};Uid={username};Pwd={password};Encrypt=yes;TrustServerCertificate=no;Connection Timeout=60;'

# Connexion à la base de données
conn = pyodbc.connect(connection_string)

# Exemple d'utilisation
cursor = conn.cursor()
cursor.execute("SELECT TOP 1* FROM Person.Person")
rows = cursor.fetchall()

for row in rows:
    print(row)

# Fermer
cursor.close()
conn.close()
