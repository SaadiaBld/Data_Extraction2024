from azure.identity import DefaultAzureCredential
from azure.storage.blob import (
    BlobServiceClient,
    BlobSasPermissions,
    generate_blob_sas,
    ContainerClient,
    UserDelegationKey,
    generate_container_sas,
    ContainerSasPermissions
)
import datetime

# # URL de ton compte Blob
# account_url = "https://datalakedeviavals.blob.core.windows.net"

# # Créer un BlobServiceClient avec l'authentification par défaut
# blob_service_client = BlobServiceClient(account_url, credential=DefaultAzureCredential())

# container_name = "data"  # Nom du conteneur blob
# container_client = blob_service_client.get_container_client(container_name)

# def request_user_delegation_key(blob_service_client: BlobServiceClient) -> UserDelegationKey:
#     """Obtenir une clé de délégation utilisateur valide pour 1 jour"""
#     delegation_key_start_time = datetime.datetime.now(datetime.timezone.utc)
#     delegation_key_expiry_time = delegation_key_start_time + datetime.timedelta(days=1)

#     user_delegation_key = blob_service_client.get_user_delegation_key(
#         key_start_time=delegation_key_start_time,
#         key_expiry_time=delegation_key_expiry_time
#     )
#     return user_delegation_key

# def create_user_delegation_sas_container(container_client: ContainerClient, user_delegation_key: UserDelegationKey):
#     """Créer un SAS de conteneur avec des permissions de lecture pour 1 jour"""
#     start_time = datetime.datetime.now(datetime.timezone.utc)
#     expiry_time = start_time + datetime.timedelta(days=1)  # Modifier selon tes besoins

#     sas_token = generate_container_sas(
#         account_name=container_client.account_name,
#         container_name=container_client.container_name,
#         user_delegation_key=user_delegation_key,
#         permission=ContainerSasPermissions(read=True, list=True),
#         expiry=expiry_time,
#         start=start_time
#     )
#     return sas_token


# try:
#     # Obtenir la User Delegation Key
#     user_delegation_key = request_user_delegation_key(blob_service_client)

#     # Générer la SAS
#     sas_token = create_user_delegation_sas_container(container_client, user_delegation_key)
#     sas_url = f"{container_client.url}?{sas_token}"
#     print(f"URL SAS générée : {sas_url}")
    
#     # Créer un ContainerClient avec l'URL SAS
#     container_client_sas = ContainerClient.from_container_url(container_url=sas_url)
#     # Lister les blobs dans le conteneur
#     print("Liste des fichiers dans le conteneur :")
#     for blob in container_client_sas.list_blobs():
#         print(blob.name)
#     # Maintenant, tu peux utiliser `container_client_sas` pour accéder au conteneur via SAS.

# except Exception as e:
#     print(f"Erreur : {e}")
#     print(f"Erreur lors de l'accès au conteneur avec SAS: {e}")


# from azure.identity import DefaultAzureCredential
# from azure.storage.blob import (
#     BlobServiceClient,
#     BlobClient,
#     generate_blob_sas,
#     BlobSasPermissions
# )
# import datetime

# # URL de ton compte Blob
# account_url = "https://datalakedeviavals.blob.core.windows.net"

# # Créer un BlobServiceClient avec l'authentification par défaut
# blob_service_client = BlobServiceClient(account_url, credential=DefaultAzureCredential())

# container_name = "data"  # Nom du conteneur blob
# blob_name = "nlp_data/etsy-reviews/Dezaart Wood Pendant Light (Design Company) - Etsy Product Reviews - English.csv"  # Nom du blob

# # Créer un client pour le blob spécifique
# blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_name)

# def generate_blob_sas_token(blob_client: BlobClient):
#     """Générer un SAS pour un blob avec des permissions de lecture"""
#     start_time = datetime.datetime.now(datetime.timezone.utc)
#     expiry_time = start_time + datetime.timedelta(hours=1)  # SAS valable pendant 1 heure

#     sas_token = generate_blob_sas(
#         account_name=blob_client.account_name,
#         container_name=blob_client.container_name,
#         blob_name=blob_client.blob_name,
#         credential=blob_client.credential,
#         permission=BlobSasPermissions(read=True),  # Permission de lecture
#         expiry=expiry_time,
#         start=start_time
#     )
#     return sas_token

# try:
#     # Générer le SAS
#     sas_token = generate_blob_sas_token(blob_client)
#     sas_url = f"{blob_client.url}?{sas_token}"
#     print(f"URL SAS générée pour le blob : {sas_url}")
    
#     # Tu peux maintenant utiliser cette URL pour accéder au blob via SAS
# except Exception as e:
#     print(f"Erreur lors de la génération du SAS: {e}")


from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient, BlobClient, generate_blob_sas, BlobSasPermissions
import datetime

# URL de ton compte Blob
account_url = "https://datalakedeviavals.blob.core.windows.net"

# Créer un BlobServiceClient avec l'authentification par défaut
blob_service_client = BlobServiceClient(account_url, credential=DefaultAzureCredential())

container_name = "data"  # Nom du conteneur blob
blob_name = "nlp_data/etsy-reviews/Dezaart Wood Pendant Light (Design Company) - Etsy Product Reviews - English.csv"  # Nom du blob

# Créer un client pour le blob spécifique
blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_name)

def generate_blob_sas_token(blob_client: BlobClient):
    """Générer un SAS pour un blob avec des permissions de lecture"""
    start_time = datetime.datetime.now(datetime.timezone.utc)
    expiry_time = start_time + datetime.timedelta(hours=1)  # SAS valable pendant 1 heure

    # Obtient la clé de délégation utilisateur via l'authentification Azure AD
    user_delegation_key = blob_service_client.get_user_delegation_key(
        key_start_time=start_time,
        key_expiry_time=expiry_time
    )

    sas_token = generate_blob_sas(
        account_name=blob_client.account_name,
        container_name=blob_client.container_name,
        blob_name=blob_client.blob_name,
        user_delegation_key=user_delegation_key,  # Utilisation de la clé de délégation utilisateur
        permission=BlobSasPermissions(read=True),  # Permission de lecture
        expiry=expiry_time,
        start=start_time
    )
    return sas_token

try:
    # Générer le SAS
    sas_token = generate_blob_sas_token(blob_client)
    sas_url = f"{blob_client.url}?{sas_token}"
    print(f"URL SAS générée pour le blob : {sas_url}")
    
    # Tu peux maintenant utiliser cette URL pour accéder au blob via SAS
except Exception as e:
    print(f"Erreur lors de la génération du SAS: {e}")
