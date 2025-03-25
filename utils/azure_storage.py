# utils/azure_storage.py
import os
import re
from azure.storage.blob import BlobServiceClient
from dotenv import load_dotenv

load_dotenv()

azure_conn_str = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
blob_service_client = BlobServiceClient.from_connection_string(azure_conn_str)
container_name = "qwasargrade"
container_client = blob_service_client.get_container_client(container_name)

def sanitize_filename(name):
    return re.sub(r'[<>:"/\\|?*]', '_', name)

def upload_to_azure(content, blob_name):
    blob_client = container_client.get_blob_client(blob_name)
    blob_client.upload_blob(content, overwrite=True)
    return blob_client.url
