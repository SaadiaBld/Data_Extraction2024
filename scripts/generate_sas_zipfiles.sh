#!/bin/bash

# Variables nécessaires
STORAGE_ACCOUNT="datalakedeviavals"   
CONTAINER_NAME="data"                 
BLOB_NAMES=("machine_learning/reviews.zip") # Fichiers à traiter
PERMISSIONS="r"                       # Permissions, ici "r" pour lecture
START_TIME=$(date -u +"%Y-%m-%dT%H:%M:%SZ")  # Heure actuelle en UTC
EXPIRY_TIME=$(date -u -d "+24 hours" +"%Y-%m-%dT%H:%M:%SZ") # Expiration dans 24 heures

# Nom du groupe de ressources Azure
RESOURCE_GROUP="RG_VANGANSBERGJ"     

# Récupérer la clé du compte de stockage via Azure CLI
ACCOUNT_KEY=$(az storage account keys list --resource-group $RESOURCE_GROUP --account-name $STORAGE_ACCOUNT --query "[0].value" --output tsv)

# Vérification si ACCOUNT_KEY a été récupéré
if [ -z "$ACCOUNT_KEY" ]; then
    echo "Erreur : Impossible de récupérer la clé d'accès pour le compte de stockage."
    exit 1
fi

# Génération du SAS Token via Azure CLI pour chaque fichier
for BLOB_NAME in "${BLOB_NAMES[@]}"; do
    SAS_TOKEN=$(az storage blob generate-sas \
        --account-name $STORAGE_ACCOUNT \
        --account-key $ACCOUNT_KEY \
        --container-name $CONTAINER_NAME \
        --name $BLOB_NAME \
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

    # Afficher l'URL SAS
    echo "URL SAS générée pour $BLOB_NAME :"
    echo $SAS_URL

    # Lancer le téléchargement automatique
    wget "$SAS_URL" -O "$(basename $BLOB_NAME)"
    if [ $? -eq 0 ]; then
        echo "Téléchargement de $BLOB_NAME réussi."
    else
        echo "Erreur lors du téléchargement de $BLOB_NAME."
    fi

    # Décompresser le fichier ZIP téléchargé
    if [[ "$(basename $BLOB_NAME)" == *.zip ]]; then
        unzip "$(basename $BLOB_NAME)" -d "extracted_files/"
        if [ $? -eq 0 ]; then
            echo "Décompression réussie pour $(basename $BLOB_NAME)."
        else
            echo "Erreur lors de la décompression de $(basename $BLOB_NAME)."
        fi
    fi

    #supprimer le fichier téléchargé (le fichier zip)
    rm "$(basename $BLOB_NAME)"
    if [ $? -eq 0 ]; then
        echo "Fichier $(basename $BLOB_NAME) supprimé avec succès."
    else
        echo "Erreur lors de la suppression du fichier $(basename $BLOB_NAME)."
    fi
done

# Parcourir le dossier "extracted_files" pour trouver des fichiers .tgz et les décompresser
for TGZ_FILE in extracted_files/*.tgz; do
    if [ -f "$TGZ_FILE" ]; then
        # Décompresser le fichier .tgz trouvé
        tar -xzvf "$TGZ_FILE" -C "extracted_files/"
        if [ $? -eq 0 ]; then
            echo "Décompression réussie pour $(basename $TGZ_FILE)."
        else
            echo "Erreur lors de la décompression de $(basename $TGZ_FILE)."
        fi
    fi
done

echo "Processus terminé."
