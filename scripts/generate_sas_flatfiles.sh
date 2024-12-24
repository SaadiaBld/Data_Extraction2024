#!/bin/bash

# Variables nécessaires
STORAGE_ACCOUNT="datalakedeviavals"   # Nom de votre compte de stockage
CONTAINER_NAME="data"                 # Nom du conteneur
REMOTE_DIR="nlp_data/"                # Dossier de départ dans le conteneur
PERMISSIONS="r"                       # Permissions, ici "r" pour lecture
START_TIME=$(date -u +"%Y-%m-%dT%H:%M:%SZ")  # Heure actuelle en UTC
EXPIRY_TIME=$(date -u -d "+24 hours" +"%Y-%m-%dT%H:%M:%SZ") # Expiration dans 24 heures

RESOURCE_GROUP="RG_VANGANSBERGJ"  

# Créer un dossier pour stocker les fichiers téléchargés
OUTPUT_DIR="nlp_data_extracted"
mkdir -p $OUTPUT_DIR

# Récupérer la clé du compte de stockage via Azure CLI
ACCOUNT_KEY=$(az storage account keys list --resource-group $RESOURCE_GROUP --account-name $STORAGE_ACCOUNT --query "[0].value" --output tsv)

if [ -z "$ACCOUNT_KEY" ]; then
    echo "Erreur : Impossible de récupérer la clé d'accès pour le compte de stockage."
    exit 1
fi

# Lister tous les blobs dans le dossier (y compris dans les sous-dossiers)
BLOB_LIST=$(az storage blob list \
    --account-name $STORAGE_ACCOUNT \
    --container-name $CONTAINER_NAME \
    --prefix $REMOTE_DIR \
    --account-key $ACCOUNT_KEY \
    --query "[].name" \
    --output tsv)

echo "***** Blobs trouvés :"
echo "$BLOB_LIST"

# Boucler sur chaque fichier et télécharger
for BLOB_NAME in $BLOB_LIST; do
    # Ignorer les répertoires (les blobs avec un nom se terminant par '/')
    if [[ "$BLOB_NAME" == */ ]]; then
        echo "Ignoré: $BLOB_NAME (répertoire virtuel)"
        continue
    fi

    # Créer le répertoire local correspondant
    LOCAL_PATH="$OUTPUT_DIR/$(dirname "${BLOB_NAME#$REMOTE_DIR}")"
    mkdir -p "$LOCAL_PATH"

    # Générer le SAS Token pour ce fichier
    SAS_TOKEN=$(az storage blob generate-sas \
        --account-name $STORAGE_ACCOUNT \
        --account-key $ACCOUNT_KEY \
        --container-name $CONTAINER_NAME \
        --name "$BLOB_NAME" \
        --permissions $PERMISSIONS \
        --start $START_TIME \
        --expiry $EXPIRY_TIME \
        --https-only \
        --output tsv)

    # Vérification si le SAS Token a été généré
    if [ -z "$SAS_TOKEN" ]; then
        echo "Erreur : Impossible de générer le SAS Token pour $BLOB_NAME."
        exit 1
    fi

    # Construction de l'URL complète avec le SAS Token
    SAS_URL="https://$STORAGE_ACCOUNT.blob.core.windows.net/$CONTAINER_NAME/$BLOB_NAME?$SAS_TOKEN"

    # Télécharger le fichier
    echo "Téléchargement de $BLOB_NAME..."
    wget "$SAS_URL" -O "$OUTPUT_DIR/$BLOB_NAME"
    
    if [ $? -eq 0 ]; then
        echo "Téléchargement réussi pour $BLOB_NAME."
    else
        echo "Erreur lors du téléchargement de $BLOB_NAME."
    fi
done

echo "Tous les fichiers ont été téléchargés dans $OUTPUT_DIR."
