# utils/canvas_integration.py
import os
from CanvasAPI import CanvasAPI
from delete_all_data import delete_all_data
from utils.azure_storage import upload_to_azure, sanitize_filename
from database.connection import get_db_connection
from dotenv import load_dotenv
import streamlit as st
import zipfile
from PyPDF2 import PdfReader
from xml.etree import ElementTree as ET
import docx
import io

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
                    # Updated file extension check
                    if ext not in ['docx', 'doc', 'txt', 'pdf', 'md', 'pages']:
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



# File handlers implementation
def read_docx(file_content):
    """Read text from DOCX files"""
    try:
        doc = docx.Document(io.BytesIO(file_content))
        return '\n'.join([para.text for para in doc.paragraphs])
    except Exception as e:
        st.error(f"DOCX read error: {str(e)}")
        return ""
    
    

def read_pdf(content):
    """Extract text from PDF files"""
    try:
        pdf = PdfReader(io.BytesIO(content))
        text = []
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text.append(page_text)
        return '\n'.join(text)
    except Exception as e:
        st.error(f"PDF read error: {str(e)}")
        return ""

def read_md(content):
    """Process Markdown files"""
    try:
        return content.decode('utf-8')
    except Exception as e:
        st.error(f"Markdown read error: {str(e)}")
        return ""

def read_pages(content):
    """Extract text from Apple Pages files"""
    try:
        with zipfile.ZipFile(io.BytesIO(content)) as z:
            for name in z.namelist():
                if name.endswith('.pdf'):
                    return read_pdf(z.read(name))
            
            xml_content = z.read('Index.xml')
            return parse_pages_xml(xml_content)
    except Exception as e:
        st.error(f"Pages file error: {str(e)}")
        return ""

def parse_pages_xml(xml_content):
    """Parse Pages XML content"""
    try:
        namespace = {'ns': 'http://developer.apple.com/namespaces/bl'}
        root = ET.fromstring(xml_content)
        text_elements = root.findall('.//ns:t', namespace)
        return '\n'.join([elem.text for elem in text_elements if elem.text])
    except Exception as e:
        st.error(f"XML parse error: {str(e)}")
        return ""
    
    
    
    
def search_files_by_student_id(student_id):
    conn = get_db_connection()
    if not conn:
        return []
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT DISTINCT file_path, file_url 
                FROM submissions 
                WHERE student_id = %s
            """, (student_id,))
            return cursor.fetchall()
    except Exception as e:
        st.error(f"Error fetching files: {e}")
        return []
    finally:
        conn.close()
        
records = {
    "jozsef.dudas@elu.nl": {"name": "Dudás József", "student_id": "403"}, "leon.aziz@elu.nl": {"name": "Leon Aziz", "student_id": "182"},
    "yana.kondratyuk@elu.nl": {"name": "Yana Kondratyuk", "student_id": "165"}, "erika.parra@elu.nl": {"name": "Erika Parra", "student_id": "464"},
    "viktor.rodau@elu.nl": {"name": "Viktor Rodau", "student_id": "181"}, "moisieiev.mykyta@elu.nl": {"name": "Moisieiev Mykyta", "student_id": "139"},
    "george.vilnoiu@elu.nl": {"name": "George Vilnoiu", "student_id": "153"}, "test_student@amsterdam.tech": {"name": "Test Student", "student_id": "464"},
    "ify@amsterdam.tech": {"name": "Ify Genevieve", "student_id": "464"}, "naz.aydin@amsterdam.tech": {"name": "Naz Aydin", "student_id": "1214"},
    "riaz.ullah@amsterdam.tech": {"name": "Riaz Ullah", "student_id": "1208"}, "ricky.benschop@amsterdam.tech": {"name": "Ricky Benschop", "student_id": "1209"},
    "isadora@amsterdam.tech": {"name": "Isadora Costa", "student_id": "2655"}
    # ... (rest of your records)
}


def get_user_details(email):
    record = records.get(email)
    return (record["name"], record["student_id"]) if record else (None, None)










# def download_course_submissions(canvas_domain, canvas_token, course_id):
#     canvas = CanvasAPI(canvas_domain, canvas_token)
#     assignments = canvas.get_course_assignments(course_id)
#     conn = get_db_connection()
#     if not conn:
#         return

#     try:
#         cursor = conn.cursor()
#         for assignment in assignments:
#             assignment_id = assignment['id']
#             assignment_name = sanitize_filename(assignment['name'])
#             submissions = canvas.get_assignment_submissions(course_id, assignment_id)
#             for submission in submissions:
#                 student_id = submission.get('user', {}).get('id', 'unknown')
#                 files = canvas.download_submission_content(submission)
#                 for filename, content in files:
#                     ext = filename.split('.')[-1].lower()
#                     if ext not in ['docx', 'txt']:
#                     # if ext not in ['docx', 'txt', 'pdf']:
#                         continue
#                     blob_name = f"{course_id}-{assignment_id}-{assignment_name}-{student_id}.{ext}"
#                     file_url = upload_to_azure(content, blob_name)
#                     cursor.execute("""
#                         INSERT INTO submissions (course_id, assignment_id, assignment_name, student_id, file_path, file_url)
#                         VALUES (%s, %s, %s, %s, %s, %s)
#                     """, (course_id, assignment_id, assignment['name'], student_id, blob_name, file_url))
#                     conn.commit()
#     except Exception as e:
#         st.error(f"Error downloading course submissions: {e}")
#     finally:
#         conn.close()
