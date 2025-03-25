# utils/security.py
import hashlib
import os
import streamlit as st
from database.connection import get_db_connection
import pandas as pd
import io


# Function to hash passwords
def hash_password(password):
    salt = os.getenv("PASSWORD_SALT", "default_salt")
    return hashlib.sha256(f"{password}{salt}".encode()).hexdigest()

# Function to validate email domain
def is_valid_email(email):
    return email.endswith("@amsterdam.tech") or email.endswith("@elu.nl")

# def is_valid_email(email):
#     return email.endswith("@amsterdam.tech")

# Function to check if username exists in the valid roles mapping
def is_valid_username(username):
    return username in role_mapping



# Function to register a new user
def register_user(email, password, role):
    if not is_valid_email(email):
        message = "Email must be from the domain @amsterdam.tech or @elu.nl"
        return False, message  # Return only the message, no Streamlit function inside the function
    
    conn = get_db_connection()
    if not conn:
        return False, "Database connection error"
    
    hashed_password = hash_password(password)
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT email FROM users WHERE email = %s", (email,))
            if cursor.fetchone():
                return False, "User with this email already exists"
            
            cursor.execute("""
                INSERT INTO users (email, password, role, is_approved) 
                VALUES (%s, %s, %s, %s)
            """, (email, hashed_password, role, False))  # Default to not approved
            conn.commit()
            return True, "User registered successfully, awaiting approval."
    except Exception as e:
        conn.rollback()
        st.error(f"Error during registration: {e}")
        return False, f"Error: {e}"
    finally:
        conn.close()

# Function to validate user login
def validate_user(email, password):
    if not is_valid_email(email):
        st.error("Invalid email format. Please use an email ending with @amsterdam.tech.")
        return None
    
    conn = get_db_connection()
    if not conn:
        st.error("Database connection error.")
        return None
    
    hashed_password = hash_password(password)
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT role, is_approved, student_id FROM users WHERE email = %s AND password = %s", (email, hashed_password))
            result = cursor.fetchone()
            if result and result[1]:  # Check if user is approved
                return result[0], result[2]  # Return role and student_id
            else:
                st.error("Invalid email or password.")
                return None, None
    except Exception as e:
        st.error(f"Error during login: {e}")
        return None, None
    finally:
        conn.close()

# Function to get all users for admin management
def get_all_users():
    conn = get_db_connection()
    if not conn:
        return []
    
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT email, role, is_approved FROM users")
            return cursor.fetchall()
    except Exception as e:
        st.error(f"Error fetching users: {e}")
        return []
    finally:
        conn.close()

      
        
        
def get_all_grading_data():
    """Retrieve all grading records from database"""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, course_id, assignment, student, file, grade, 
                   feedback, suggestions, instructor_comment, timestamp 
            FROM grading_records
        """)
        return cursor.fetchall()  # Returns list of tuples
    except Exception as e:
        print(f"Database error: {str(e)}")
        return []
    finally:
        if conn:
            conn.close()



# Function to generate an Excel report from grading data
import pandas as pd
import io

def generate_excel_report(grading_data):
    """
    Generate an Excel report from the grading data.

    Args:
        grading_data (list of dict): List containing grading information.

    Returns:
        bytes: The Excel file content in bytes, or None if no data is provided.

    Raises:
        KeyError: If one or more required columns are missing.
    """
    # Define the required columns in the desired order.
    required_columns = [
        "ID", "Course ID", "Assignment", "Student",
        "File", "Grade", "Feedback", "Suggestions", "Timestamp"
    ]

    # Convert grading data to DataFrame.
    df = pd.DataFrame(grading_data)

    # Check if the DataFrame is empty.
    if df.empty:
        return None

    # Add a serial number column at the beginning.
    df.insert(0, 'S/N', range(1, len(df) + 1))

    # Verify that all required columns exist in the DataFrame.
    missing_cols = set(required_columns) - set(df.columns)
    if missing_cols:
        raise KeyError(f"Missing required columns: {', '.join(missing_cols)}")
    
    # Reorder the DataFrame columns.
    df = df[required_columns]

    # Convert any unsupported data types to string.
    # This helps avoid issues when writing cells with unexpected types.
    df = df.applymap(lambda x: str(x) if not isinstance(x, (int, float, str, bool)) and x is not None else x)

    # Create a BytesIO buffer to hold the Excel data.
    output = io.BytesIO()

    # Write the DataFrame to an Excel file using the xlsxwriter engine.
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Grades')

    # Retrieve and return the Excel file content in bytes.
    return output.getvalue()



# utils/security.py
import pandas as pd

def generate_excel_report(data_dict):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        for sheet_name, df in data_dict.items():
            # Convert timezone-aware datetimes to naive
            for col in df.columns:
                if pd.api.types.is_datetime64_any_dtype(df[col]):
                    df[col] = df[col].dt.tz_localize(None)
            df.to_excel(writer, sheet_name=sheet_name, index=False)
    return output.getvalue()

