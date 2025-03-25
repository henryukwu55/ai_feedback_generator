import streamlit as st
import pandas as pd
from database.connection import get_db_connection



# Function to get all users for admin management
        
# In database/operations.py
def get_all_users():
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT email, role, is_approved, created_at FROM users")
            return cursor.fetchall()
    finally:
        conn.close()
        

# Function to approve a user
def approve_user(email):
    conn = get_db_connection()
    if not conn:
        return False, "Database connection error"
    
    try:
        with conn.cursor() as cursor:
            cursor.execute("UPDATE users SET is_approved = TRUE WHERE email = %s", (email,))
            conn.commit()
            return True, "User approved successfully."
    except Exception as e:
        conn.rollback()
        return False, f"Error approving user: {e}"
    finally:
        conn.close()



# Function to fetch assignments for a specific student using their student ID
def fetch_student_assignments(student_id):
    conn = get_db_connection()
    if not conn:
        return []
    
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT assignment_name
                FROM submissions 
                WHERE student_id = %s
            """, (student_id,))
            return cursor.fetchall()
    except Exception as e:
        st.error(f"Error fetching assignments: {e}")
        return []
    finally:
        conn.close()

# Function to search for files using student ID
def search_files_by_student_id(student_id):
    conn = get_db_connection()
    if not conn:
        return []
    
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT file_path, file_url 
                FROM submissions 
                WHERE student_id = %s
            """, (student_id,))
            return cursor.fetchall()
    except Exception as e:
        st.error(f"Error fetching files: {e}")
        return []
    finally:
        conn.close()
        
        


# database/operations.py

def save_feedback_to_db(student_id, course_id, assignment_id, file_path, feedback, suggestions):
    """
    Save accepted feedback to PostgreSQL database.
    
    Args:
        student_id: Student ID string
        course_id: Course ID string
        assignment_id: Assignment ID string
        file_path: File path string
        feedback: Feedback text
        suggestions: Suggestions text
    
    Returns:
        bool: True if successful, False otherwise
    """
    conn = None
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute("""
                INSERT INTO feedback (
                    student_id, 
                    course_id, 
                    assignment_id, 
                    file_path, 
                    feedback, 
                    suggestions
                )
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (
                student_id,
                course_id,
                assignment_id,
                file_path,
                feedback,
                suggestions
            ))
            conn.commit()
            return True
    except Exception as e:
        st.error(f"Database Error: {str(e)}")
        if conn:
            conn.rollback()
        return False
    finally:
        if conn:
            conn.close()


# database/operations.py

def get_accepted_feedback(student_id):
    """
    Retrieve feedback accepted in the last hour for a student
    """
    conn = None
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT 
                    student_id,
                    course_id,
                    assignment_id,
                    file_path,
                    feedback,
                    suggestions,
                    created_at
                FROM feedback
                WHERE student_id = %s
                AND created_at >= NOW() - INTERVAL '1 HOUR'
                ORDER BY created_at DESC
            """, (student_id,))
            
            columns = [desc[0] for desc in cursor.description]
            data = cursor.fetchall()
            
            if data:
                return pd.DataFrame(data, columns=columns)
            return pd.DataFrame()
            
    except Exception as e:
        st.error(f"Database Error: {str(e)}")
        return pd.DataFrame()
    finally:
        if conn:
            conn.close()



# Add this function to database/operations.py
def get_grading_records(time_filter='last_hour'):
    """Retrieve grading records based on time filter"""
    intervals = {
        'last_hour': "1 HOUR",
        'last_day': "1 DAY",
        'last_week': "1 WEEK",
        'last_month': "1 MONTH",
        'last_year': "1 YEAR",
        'all_time': None
    }
    
    conn = None
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            base_query = """
                SELECT course_id, assignment, student, file, grade, 
                       feedback, suggestions, instructor_comment, timestamp 
                FROM grading_records
            """
            
            if intervals[time_filter]:
                query = base_query + " WHERE timestamp >= NOW() - INTERVAL %s"
                cursor.execute(query, (intervals[time_filter],))
            else:
                cursor.execute(base_query)

            columns = [desc[0] for desc in cursor.description]
            data = cursor.fetchall()
            
            return pd.DataFrame(data, columns=columns) if data else pd.DataFrame()
            
    except Exception as e:
        st.error(f"Database Error: {str(e)}")
        return pd.DataFrame()
    finally:
        if conn:
            conn.close()
            
            
            
# database/operations.py

def delete_user(email):
    """Delete a user from the database"""
    conn = None
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute("DELETE FROM users WHERE email = %s", (email,))
            conn.commit()
            return True, f"User {email} deleted successfully"
    except Exception as e:
        return False, f"Error deleting user: {str(e)}"
    finally:
        if conn:
            conn.close()
            
            
            
# pages/1_🧑‍💼_Admin_Dashboard.py

def handle_delete(email):
    """Handle user deletion"""
    success, message = delete_user(email)
    if success:
        st.success(message)
    else:
        st.error(message)
    st.rerun()
    



def get_user_id_by_username(username):
    """
    Get user ID from database using username/email
    Returns: user_id (str) or None if not found
    """
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT user_id FROM users 
                WHERE username = %s
            """, (username,))
            result = cursor.fetchone()
            return result[0] if result else None
    except Exception as e:
        print(f"User ID lookup error: {str(e)}")
        return None
    finally:
        conn.close()


def update_user_approval(user_id: int, is_approved: bool):
    """Update user approval status in database"""
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                UPDATE users
                SET is_approved = %s
                WHERE user_id = %s
            """, (is_approved, user_id))
            conn.commit()
        return True
    except Exception as e:
        st.error(f"Error updating user {user_id}: {str(e)}")
        return False
    finally:
        conn.close()
        
        
        
def save_user_approvals():
    """Save approval changes to database"""
    if 'edited_users' in st.session_state:
        try:
            # Get changed rows
            changed_users = st.session_state.edited_users[
                st.session_state.edited_users['is_approved'] != users_df['is_approved']
            ]
            
            # Update database
            for _, row in changed_users.iterrows():
                success = update_user_approval(
                    user_id=row['user_id'],
                    is_approved=row['is_approved']
                )
                if not success:
                    st.error(f"Failed to update user {row['user_id']}")
                    return
            
            st.success("Approvals updated successfully!")
            st.rerun()  # Refresh data
            
        except Exception as e:
            st.error(f"Error saving approvals: {str(e)}")     
            



from database.connection import get_db_connection  # Your DB connection function

def fetch_users():
    conn = get_db_connection()
    users_df = pd.read_sql(
        "SELECT email, role, is_approved, created_at FROM users",  # Use exact column names
        conn
    )
    conn.close()
    return users_df

def update_user_approvals_in_db(updates):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        for _, row in updates.iterrows():
            cursor.execute(
                "UPDATE users SET is_approved = %s WHERE email = %s",  # Match schema
                (row['is_approved'], row['email'])
            )
        conn.commit()
        st.success("✅ Approvals updated successfully!")
    except Exception as e:
        conn.rollback()
        st.error(f"🚨 Database error: {str(e)}")
    finally:
        cursor.close()
        conn.close()
        
        

def get_admin_metrics():
    """Get key metrics for admin dashboard"""
    conn = None
    try:
        conn = get_db_connection()
        if not conn:
            st.error("Failed to connect to database")
            return None
            
        with conn.cursor() as cursor:
            # Total Users
            cursor.execute("SELECT COUNT(*) FROM users")
            total_users = cursor.fetchone()[0]

            # Graded Assignments
            cursor.execute("SELECT COUNT(*) FROM grading_records")
            graded_assignments = cursor.fetchone()[0]

            # Active Courses
            cursor.execute("SELECT COUNT(DISTINCT course_id) FROM submissions")
            active_courses = cursor.fetchone()[0]

            return {
                'total_users': total_users,
                'graded_assignments': graded_assignments,
                'active_courses': active_courses,
                'system_uptime': 99.98  # Placeholder for actual uptime monitoring
            }
            
    except Exception as e:
        st.error(f"Database error: {str(e)}")
        return None
    finally:
        if conn:
            conn.close()