import os
import pandas as pd
from PIL import Image
import io


parquet_files_dir = './parquet_files'

# Créer un dossier 'images' pour stocker les fichiers
os.makedirs("images", exist_ok=True)

#créer un dossier metadata pour stocker les metadonnées
os.makedirs("metadata", exist_ok=True)

#lister fichiers parquet dans dossier  parquet_files
parquet_files = [file for file in os.listdir(parquet_files_dir)if file.endswith('.parquet')]

image_format = 'png'  # Changez en 'jpeg' si vous voulez ce format

for parquet_file_name in parquet_files:
    subfolder_name, _, _ = parquet_file_name.partition('.')
    os.makedirs(f'images/{subfolder_name}', exist_ok=True)

    df = pd.read_parquet(f'{parquet_files_dir}/{parquet_file_name}')
    # Liste pour stocker les chemins des images générées
    image_paths = []

    # Extraire et sauvegarder les images avec item_ID
    for idx, row in df.iterrows():
    # Récupérer les données binaires de l'image et l'item_ID
        image_bytes = row['image']['bytes']  # Données binaires de l'image
        item_id = row['item_ID']             # ID unique de l'image
    
        # Convertir les bytes en image
        image = Image.open(io.BytesIO(image_bytes))
    
        # Si l'image est en mode RGBA (avec transparence), convertir en RGB pour JPEG
        if image.mode == 'RGBA' and image_format == 'jpeg':
            image = image.convert('RGB')
    
        # Définir le chemin de sauvegarde avec le format choisi
        image_path = f"images/{subfolder_name}/{item_id}.{image_format}"
    
        # Sauvegarder l'image dans le format spécifié
        image.save(image_path, format=image_format.upper())
    
        # Ajouter le chemin de l'image à la liste
        image_paths.append(image_path)

    # Ajouter les chemins des images dans le DataFrame pour l'export CSV
    df['image_path'] = image_paths

    #nom du dossier 
    metadata_filename = f"metadata/metadata_{subfolder_name}.csv"

    # Exporter les métadonnées dans un fichier CSV
    df[['item_ID', 'query', 'title', 'position', 'image_path']].to_csv(metadata_filename, index=False)

    print(f"Les images du fichier {parquet_file_name} ont été sauvegardées dans 'images/{subfolder_name}/' en format {image_format.upper()} et les métadonnées dans '{metadata_filename}'.")