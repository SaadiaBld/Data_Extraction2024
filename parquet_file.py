from azure.identity import DefaultAzureCredential
from azure.storage.blob import (
    BlobServiceClient,
    ContainerClient,
    BlobClient,
    BlobSasPermissions,
    ContainerSasPermissions,
    UserDelegationKey,
    generate_container_sas,
    generate_blob_sas
)
import datetime

#pour obtenur un token que le script utilisera pour pouvoir requeter le Blob storage, créer une instance de DefaultAzureCredential
# cf https://learn.microsoft.com/en-us/azure/storage/blobs/storage-blob-user-delegation-sas-create-python?tabs=container
# Construct the blob endpoint from the account name
account_url = "https://<storage-account-name>.blob.core.windows.net"

#Create a BlobServiceClient object using DefaultAzureCredential
blob_service_client = BlobServiceClient(account_url, credential=DefaultAzureCredential())

container_name = "data"  # Nom du conteneur blob
container_client = blob_service_client.get_container_client(container_name)

#pour generer une sas securisée, il faut une user delegation key et des infos sur les permissions (accées lecture, ecriture,.., et durée de validité)
def request_user_delegation_key(blob_service_client: BlobServiceClient) -> UserDelegationKey:
    # Get a user delegation key that's valid for 1 day
    delegation_key_start_time = datetime.datetime.now(datetime.timezone.utc)
    delegation_key_expiry_time = delegation_key_start_time + datetime.timedelta(days=1)

    user_delegation_key = blob_service_client.get_user_delegation_key(
        key_start_time=delegation_key_start_time,
        key_expiry_time=delegation_key_expiry_time
    )
    return user_delegation_key

def create_user_delegation_sas_container(container_client: ContainerClient, user_delegation_key: UserDelegationKey):
    # Create a SAS token that's valid for one day, as an example
    start_time = datetime.datetime.now(datetime.timezone.utc)
    expiry_time = start_time + datetime.timedelta(days=1)

    sas_token = generate_container_sas(
        account_name=container_client.account_name,
        container_name=container_client.container_name,
        user_delegation_key=user_delegation_key,
        permission=ContainerSasPermissions(read=True),
        expiry=expiry_time,
        start=start_time
    )
    return sas_token


#utiliser le user delegation SAS pour authoriser lun client object
# The SAS token string can be appended to the resource URL with a ? delimiter
# or passed as the credential argument to the client constructor
# sas_url = f"{container_client.url}?{sas_token}"

# # Create a ContainerClient object with SAS authorization
# container_client_sas = ContainerClient.from_container_url(container_url=sas_url)

try:
    # Obtenir la User Delegation Key
    user_delegation_key = request_user_delegation_key(blob_service_client)

    # Générer la SAS
    sas_token = create_user_delegation_sas_container(container_client, user_delegation_key)
    sas_url = f"{container_client.url}?{sas_token}"
    print(f"URL SAS générée : {sas_url}")
    
    # Créer un ContainerClient avec l'URL SAS
    container_client_sas = ContainerClient.from_container_url(container_url=sas_url)

except Exception as e:
    print(f"Erreur : {e}")
