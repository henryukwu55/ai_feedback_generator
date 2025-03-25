# utils/canvas_integration.py
import os
from CanvasAPI import CanvasAPI
from delete_all_data import delete_all_data
from utils.azure_storage import upload_to_azure, sanitize_filename
from database.connection import get_db_connection
from dotenv import load_dotenv
import streamlit as st

load_dotenv()

canvas_token = os.getenv("CANVAS_TOKEN")

# Function to fetch submissions
def fetch_submissions(canvas_domain, course_id):
    """
    Delete all data on submissions table
    Fetch course submissions from Canvas.

    Args:
        canvas_domain (str): The Canvas instance domain.
        course_id (str): The ID of the course.

    Returns:
        None
    """
    
    import os
    import psycopg2
    from azure.storage.blob import BlobServiceClient
    from dotenv import load_dotenv

    # Load environment variables from .env file
    load_dotenv()

    # Azure Blob Storage Configuration
    AZURE_CONNECTION_STRING = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
    BLOB_CONTAINER_NAME = os.getenv("CONTAINER_NAME")

    # PostgreSQL Database Configuration
    DB_CONNECTION = {
     "dbname": os.getenv("POSTGRESQL_DATABASE"),
     "user": os.getenv("POSTGRESQL_USER"),
     "password": os.getenv("POSTGRESQL_PASSWORD"),
     "host": os.getenv("POSTGRESQL_HOST"),
     "port": os.getenv("POSTGRESQL_PORT"),
     }

     # Connect to Azure Blob Storage
    blob_service_client = BlobServiceClient.from_connection_string(AZURE_CONNECTION_STRING)
    container_client = blob_service_client.get_container_client(BLOB_CONTAINER_NAME)
    
    
    
    if not canvas_domain:
        canvas_domain = os.getenv("CANVAS_DOMAIN")
    if not course_id:
        course_id = os.getenv("COURSE_ID")

    if not canvas_domain or not course_id:
        raise ValueError("Canvas domain and course ID must be provided.")

    """Fetch course submissions from Canvas."""
    if canvas_domain and course_id:
        with st.spinner("Fetching submissions..."):
            delete_all_data(container_client, psycopg2, DB_CONNECTION)
            try:
                download_course_submissions(canvas_domain, canvas_token, course_id)
                st.success("Submissions downloaded successfully!")
            except Exception as e:
                st.error(f"Download failed: {str(e)}")
    else:
        st.error("Missing required credentials")

def download_course_submissions(canvas_domain, canvas_token, course_id):
    canvas = CanvasAPI(canvas_domain, canvas_token)
    assignments = canvas.get_course_assignments(course_id)
    conn = get_db_connection()
    if not conn:
        return

    try:
        cursor = conn.cursor()
        for assignment in assignments:
            assignment_id = assignment['id']
            assignment_name = sanitize_filename(assignment['name'])
            submissions = canvas.get_assignment_submissions(course_id, assignment_id)
            for submission in submissions:
                student_id = submission.get('user', {}).get('id', 'unknown')
                files = canvas.download_submission_content(submission)
                for filename, content in files:
                    ext = filename.split('.')[-1].lower()
                    if ext not in ['docx', 'txt']:
                    # if ext not in ['docx', 'txt', 'pdf']:
                        continue
                    blob_name = f"{course_id}-{assignment_id}-{assignment_name}-{student_id}.{ext}"
                    file_url = upload_to_azure(content, blob_name)
                    cursor.execute("""
                        INSERT INTO submissions (course_id, assignment_id, assignment_name, student_id, file_path, file_url)
                        VALUES (%s, %s, %s, %s, %s, %s)
                    """, (course_id, assignment_id, assignment['name'], student_id, blob_name, file_url))
                    conn.commit()
    except Exception as e:
        st.error(f"Error downloading course submissions: {e}")
    finally:
        conn.close()
