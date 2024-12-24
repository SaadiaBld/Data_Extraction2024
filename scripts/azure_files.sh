#!/bin/bash

# === Configuration des variables ===
STORAGE_ACCOUNT="datalakedeviavals"   # Nom du compte de stockage
CONTAINER_NAME="data"                # Nom du conteneur
RESOURCE_GROUP="RG_VANGANSBERGJ"     # Nom du groupe de ressources
LOCAL_DIR="./nlp_data"               # Répertoire local pour les téléchargements
EXPIRY_TIME=$(date -u -d "+24 hours" +"%Y-%m-%dT%H:%M:%SZ") # Expiration dans 24h

# Créez le répertoire local si nécessaire
mkdir -p "$LOCAL_DIR"

# Vérifie si AzCopy est installé
if ! command -v azcopy &> /dev/null; then
    echo "Erreur : AzCopy n'est pas installé. Installez-le avant d'exécuter ce script."
    exit 1
fi

# Récupération de la clé d'accès du compte de stockage
echo "Récupération de la clé d'accès pour le compte de stockage..."
ACCOUNT_KEY=$(az storage account keys list --resource-group "$RESOURCE_GROUP" --account-name "$STORAGE_ACCOUNT" --query "[0].value" --output tsv)

# Vérification si ACCOUNT_KEY a été récupéré
if [ -z "$ACCOUNT_KEY" ]; then
    echo "Erreur : Impossible de récupérer la clé d'accès pour le compte de stockage."
    exit 1
fi

# Récupération des blobs CSV
echo "Récupération des blobs dans le conteneur Azure..."
# 
BLOBS=$(az storage blob list --account-name "$STORAGE_ACCOUNT" --account-key "$ACCOUNT_KEY" --container-name "$CONTAINER_NAME" \
     --query "[?starts_with(name, 'nlp_data/') && ends_with(name, '.csv')].name" --output tsv)


# Vérification si des blobs existent
if [ -z "$BLOBS" ]; then
    echo "Aucun blob trouvé dans le conteneur $CONTAINER_NAME."
    exit 1
fi

# Génération d'un SAS Token
echo "Génération d'un SAS Token pour un accès temporaire..."
SAS_TOKEN=$(az storage container generate-sas --account-name "$STORAGE_ACCOUNT" --name "$CONTAINER_NAME" --permissions rl --expiry "$EXPIRY_TIME" --output tsv)

# Fonction pour encoder les URLs
urlencode() {
    local STRING="$1"
    local ENCODED=""
    local i
    for (( i=0; i<${#STRING}; i++ )); do
        local CHAR="${STRING:$i:1}"
        case "$CHAR" in
            [a-zA-Z0-9.~_,-]) ENCODED+="$CHAR" ;;  # Inclure l'apostrophe et la virgule
            *) ENCODED+=$(printf '%%%02X' "'$CHAR") ;;  # Encodage des autres caractères
        esac
    done
    echo "$ENCODED"
}

# Fonction pour télécharger un blob spécifique
download_blob() {
    local BLOB="$1"
    
    # Encodage du nom du blob pour l'URL
    ENCODED_BLOB=$(urlencode "$BLOB")
    
    # Suppression du préfixe `nlp_data/` dans le chemin local
    LOCAL_PATH="$LOCAL_DIR/$(echo "$BLOB" | sed 's/^nlp_data\///')"
    
    # Création des répertoires locaux nécessaires
    mkdir -p "$(dirname "$LOCAL_PATH")"
    
    echo "Téléchargement de : $BLOB"
    azcopy copy "$SAS_URL" "$LOCAL_PATH" --recursive --overwrite=true
    
    # Vérification du succès du téléchargement
    if [ $? -ne 0 ]; then
        echo "Erreur lors du téléchargement de $BLOB. Le script continue avec les autres fichiers."
    else
        echo "Téléchargement réussi : $BLOB"
    fi
}
# Génération de l'URL complète pour le blob
SAS_URL="https://$STORAGE_ACCOUNT.blob.core.windows.net/$CONTAINER_NAME/$BLOB_NAME?$SAS_TOKEN"
    
# Téléchargement de tous les fichiers CSV
echo "Téléchargement des fichiers CSV..."
while IFS= read -r BLOB; do
    # Filtrage des blobs qui ont un nom CSV
    if [[ "$BLOB" =~ \.csv$ ]]; then
        download_blob "$BLOB"
    fi
done <<< "$BLOBS"

echo "Téléchargement terminé. Tous les fichiers CSV valides ont été enregistrés dans $LOCAL_DIR."
