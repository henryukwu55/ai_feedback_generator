# utils/session.py
import streamlit as st
import uuid
from datetime import datetime
import pandas as pd
from database.connection import get_db_connection


def initialize_session():
    """Initialize session state variables."""
    session_defaults = {
        "logged_in": False,
        "username": None,
        "role": None,
        "session_id": None,
        "login_time": None,
        "last_activity": None,
        "grading_data": []
    }
    for key, default_value in session_defaults.items():
        if key not in st.session_state:
            st.session_state[key] = default_value
            
            
# utils/session.py
def save_session_to_db(user_id, role, session_id, login_time):
    """PROPERLY updates sessions table in PostgreSQL"""
    conn = get_db_connection()
    if conn:
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO sessions 
                        (session_id, user_id, role, login_time, is_active)
                    VALUES (%s, %s, %s, %s, TRUE)
                    ON CONFLICT (user_id) DO UPDATE SET
                        session_id = EXCLUDED.session_id,
                        login_time = EXCLUDED.login_time,
                        is_active = TRUE
                """, (session_id, user_id, role, login_time))
                conn.commit()
        except Exception as e:
            st.error(f"Session save failed: {e}")
        finally:
            conn.close()

def set_user_session(username, role):
    """
    Set the user's session state upon successful login.
    
    Args:
        username (str): The username of the logged-in user.
        role (str): The role assigned to the user.
    """
    st.session_state.logged_in = True
    st.session_state.username = username
    st.session_state.role = role
    st.session_state.session_id = str(uuid.uuid4())
    st.session_state.login_time = datetime.now()
    save_session_to_db(username, role, st.session_state.session_id, st.session_state.login_time)

# def clear_session():
#     """Clear the user's session state upon logout."""
#     for key in list(st.session_state.keys()):
#         del st.session_state[key]

def clear_session():
    """Clear the user's session state upon logout."""
    if st.session_state.get("username"):
        end_session(st.session_state.username)  # Add this line
    for key in list(st.session_state.keys()):
        del st.session_state[key]


def save_session(username, role):
    """
    Save the user's session details to the database.

    Args:
        username (str): The username of the logged-in user.
        role (str): The role assigned to the user.

    Returns:
        str: The generated session ID.
    """
    session_id = str(uuid.uuid4())
    login_time = datetime.now()
    conn = get_db_connection()
    if conn:
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO sessions (user_id, role, session_id, login_time)
                    VALUES (%s, %s, %s, %s)
                    ON CONFLICT (user_id) DO UPDATE
                    SET session_id = EXCLUDED.session_id, login_time = EXCLUDED.login_time
                """, (username, role, session_id, login_time))
                conn.commit()
            return session_id
        except Exception as e:
            st.error(f"Error saving session to database: {e}")
            return None
        finally:
            conn.close()
    else:
        st.error("Database connection failed.")
        return None


from datetime import datetime, timedelta

def update_active_session(username, role):
    """Create or update session record"""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO sessions (user_id, role, login_time, last_activity, is_active)
            VALUES (%s, %s, NOW(), NOW(), TRUE)
            ON CONFLICT (user_id) 
            DO UPDATE SET 
                last_activity = NOW(),
                is_active = TRUE
        """, (username, role))
        conn.commit()
    finally:
        conn.close()



def end_session(user_id):
    """Mark session as inactive"""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE sessions 
            SET is_active = FALSE 
            WHERE user_id = %s
        """, (user_id,))
        conn.commit()
    finally:
        conn.close()


        

def get_active_sessions():
    """Get currently active sessions with real-time status"""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT session_id, user_id, role, login_time, last_activity 
            FROM sessions 
            WHERE is_active = TRUE
            AND last_activity > NOW() - INTERVAL '5 minutes'
        """)
        return cursor.fetchall()
    finally:
        conn.close()

def restrict_access(allowed_roles):
    """
    Restrict page access based on user roles.
    
    Args:
        allowed_roles (list): A list of roles permitted to access the page.
    """
    if not st.session_state.logged_in:
        st.error("You must be logged in to view this page.")
        st.stop()
    elif st.session_state.role not in allowed_roles:
        st.error("You do not have permission to view this page.")
        st.stop()


# utils/session.py
def create_session(user_id: int) -> str:
    """Create new session with initial timestamps"""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        session_id = str(uuid.uuid4())
        
        cursor.execute("""
            INSERT INTO sessions 
                (session_id, user_id, login_time, last_activity)
            VALUES (%s, %s, NOW(), NOW())
        """, (session_id, user_id))
        
        conn.commit()
        return session_id
    except Exception as e:
        conn.rollback()
        st.error(f"Session creation failed: {str(e)}")
        return None
    finally:
        conn.close()
        
    
# utils/session.py
def update_activity():
    """Update last_activity timestamp for active sessions"""
    if "user_id" in st.session_state and "session_id" in st.session_state:
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE sessions
                SET last_activity = NOW()
                WHERE user_id = %s AND session_id = %s
            """, (st.session_state.user_id, st.session_state.session_id))
            conn.commit()
        except Exception as e:
            st.error(f"Activity update failed: {str(e)}")
        finally:
            conn.close()

   
# utils/session.py
def clean_inactive_sessions():
    """Automatically mark inactive sessions"""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE sessions 
            SET is_active = FALSE 
            WHERE last_activity < NOW() - INTERVAL '15 minutes'
        """)
        conn.commit()
    finally:
        conn.close()

