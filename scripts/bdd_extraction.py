import os
from dotenv import load_dotenv
import pyodbc
import csv

load_dotenv()

# Variables d'environnement à récupérer
server = os.getenv('AZURE_SQL_SERVER')
database = os.getenv('AZURE_SQL_DATABASE')
username = os.getenv('AZURE_SQL_USERNAME')
password = os.getenv('AZURE_SQL_PASSWORD')


#connection_string = os.getenv("AZURE_SQL_CONNECTIONSTRING")
connection_string = f'Driver={{ODBC Driver 18 for SQL Server}};Server=tcp:{server},1433;Database={database};Uid={username};Pwd={password};Encrypt=yes;TrustServerCertificate=no;Connection Timeout=60;'

# se connecter à la bdd
conn = pyodbc.connect(connection_string)
print('Connexion réussie')

cursor = conn.cursor()
cursor.execute("SELECT table_schema, table_name FROM information_schema.tables WHERE (table_schema LIKE 'Person%' or table_schema LIKE 'Production%' or table_schema LIKE 'Sales%') AND TABLE_TYPE ='BASE TABLE'")
rows = cursor.fetchall()
print(f"Nombre de tables : {len(rows)}")

directory = "/home/utilisateur/Documents/devia_2425/db_files"

for row in rows:
    table_schema=row[0]
    table_name=row[1]
    print(f'table_schema: {table_schema}, table_name:{table_name}')

def create_filename(table_schema, table_name, extension='csv'):
    file_name=table_schema +'_'+ table_name +'.'+extension
    return file_name
    

def write_to_csv(records, filename):
    os.makedirs(directory, exist_ok=True)
    with open(filename, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(records)

def main():
    for row in rows:
        table_schema = row[0]
        table_name = row[1]
        print(f'Récuperer des données de la table: {table_schema}.{table_name}')

        try:
            cursor.execute(f'SELECT * FROM {table_schema}.{table_name}')
            records = cursor.fetchall()
            if records:
                filename=os.path.join(directory, create_filename(table_schema, table_name))

                write_to_csv(records, filename)
                #print(f'Les données de {table_schema}.{table_name} ont été enregistrées dans {filename}')
            else:
                print(f'Aucune donnée trouvée pour la table {table_schema}.{table_name}')
        except Exception as e:
                print(f"Erreur lors de la récupération des données de {table_schema}.{table_name}: {e}")

if __name__ == "__main__":
    main()

# Fermer
cursor.close()
conn.close()







