def delete_all_data(container_client, psycopg2, DB_CONNECTION):
    """Deletes all blobs in Azure Storage and clears the PostgreSQL table."""
    
    # Delete all blobs in the Azure container
    blobs = container_client.list_blobs()
    for blob in blobs:
        container_client.delete_blob(blob.name)
        print(f"Deleted Blob: {blob.name}")

    # Delete all records in the PostgreSQL table
    conn = psycopg2.connect(**DB_CONNECTION)
    cur = conn.cursor()
    
    cur.execute("TRUNCATE TABLE submissions RESTART IDENTITY;")  # Clears data and resets primary key ID
    conn.commit()
    
    cur.close()
    conn.close()
    
    print("PostgreSQL table data deleted.")
    print("All files deleted from Azure and database table cleared!")

# Call the single function
# delete_all_data()





# import os
# import psycopg2
# from azure.storage.blob import BlobServiceClient
# from dotenv import load_dotenv

# # Load environment variables from .env file
# load_dotenv()

# # Azure Blob Storage Configuration
# AZURE_CONNECTION_STRING = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
# BLOB_CONTAINER_NAME = os.getenv("CONTAINER_NAME")

# # PostgreSQL Database Configuration
# DB_CONNECTION = {
#     "dbname": os.getenv("POSTGRESQL_DATABASE"),
#     "user": os.getenv("POSTGRESQL_USER"),
#     "password": os.getenv("POSTGRESQL_PASSWORD"),
#     "host": os.getenv("POSTGRESQL_HOST"),
#     "port": os.getenv("POSTGRESQL_PORT"),
# }

# # Connect to Azure Blob Storage
# blob_service_client = BlobServiceClient.from_connection_string(AZURE_CONNECTION_STRING)
# container_client = blob_service_client.get_container_client(BLOB_CONTAINER_NAME)

# def delete_all_blobs():
#     """Deletes all files in the Azure Blob Storage container"""
#     blobs = container_client.list_blobs()
#     for blob in blobs:
#         container_client.delete_blob(blob.name)
#         print(f"Deleted: {blob.name}")

# def delete_all_records():
#     """Deletes all records from the PostgreSQL table"""
#     conn = psycopg2.connect(**DB_CONNECTION)
#     cur = conn.cursor()
    
#     cur.execute("TRUNCATE TABLE submissions RESTART IDENTITY;")  # Clears data and resets primary key ID
#     conn.commit()
    
#     cur.close()
#     conn.close()
#     print("PostgreSQL table data deleted.")

# # Run both cleanup functions
# delete_all_blobs()
# delete_all_records()
# print("All files deleted from Azure and database table cleared!")
