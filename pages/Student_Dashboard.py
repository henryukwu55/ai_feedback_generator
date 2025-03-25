import streamlit as st
# st.set_page_config(
#     page_title="SmartAssess",
#     page_icon="📝",
#     layout="wide",
#     initial_sidebar_state="expanded"
# )

import docx
import io
import pandas as pd
import requests
import json
from utils.session import initialize_session, restrict_access, update_activity
from database.connection import get_db_connection
from utils.grading import fetch_assignment_rubric, get_ai_feedback_student, convert_rubric_to_table, save_grading_record_student, get_all_grading_data_student
from utils.azure_storage import *
from database.operations import fetch_student_assignments, save_feedback_to_db, get_accepted_feedback
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


# Add to the top of every page/script
def track_activity():
    if st.session_state.get("logged_in"):
        update_activity()


# Theme-aware styling
current_theme = st.get_option("theme.base")
if current_theme == "dark":
    st.markdown("""
        <style>
            /* Dark mode text areas and inputs */
            [data-testid="stTextArea"] textarea,
            [data-testid="stTextInput"] input,
            [data-testid="stNumberInput"] input {
                background-color: #2D2D2D !important;
                color: #FFFFFF !important;
                border: 1px solid #555555 !important;
            }
            
            /* Dark mode suggestions box */
            .stTextArea textarea:focus {
                border-color: #4A90E2 !important;
                box-shadow: 0 0 0 0.2rem rgba(74, 144, 226, 0.25) !important;
            }
        </style>
    """, unsafe_allow_html=True)

# Common styling for both themes
st.markdown(
    """
    <style>
    /* Button styling */
    div.stButton > button {
        background-color: grey !important;
        color: white !important;
        border: none !important;
        transition: all 0.3s ease !important;
    }
    
    div.stButton > button:hover {
        opacity: 0.8 !important;
        transform: scale(1.05) !important;
    }

    /* Expander styling */
    [data-testid="expander"] > div:first-child {
        background-color: grey !important;
        color: white !important;
        border-radius: 8px !important;
    }
    
    [data-testid="stExpander"] > div:nth-child(2) {
        background-color: rgba(128, 128, 128, 0.1) !important;
        border-radius: 8px !important;
        padding: 1rem !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

#*****************************
# Full data stored as a dictionary of dictionaries
records = {
    "jozsef.dudas@elu.nl": {"name": "Dudás József", "student_id": "403"}, "leon.aziz@elu.nl": {"name": "Leon Aziz", "student_id": "182"},
    "yana.kondratyuk@elu.nl": {"name": "Yana Kondratyuk", "student_id": "165"}, "erika.parra@elu.nl": {"name": "Erika Parra", "student_id": "464"},
    "viktor.rodau@elu.nl": {"name": "Viktor Rodau", "student_id": "181"}, "moisieiev.mykyta@elu.nl": {"name": "Moisieiev Mykyta", "student_id": "139"},
    "george.vilnoiu@elu.nl": {"name": "George Vilnoiu", "student_id": "153"}, "test_student@amsterdam.tech": {"name": "Test Student", "student_id": "464"},
    "ify@amsterdam.tech": {"name": "Ify Genevieve", "student_id": "464"}, "naz.aydin@amsterdam.tech": {"name": "Naz Aydin", "student_id": "1214"},
    "riaz.ullah@amsterdam.tech": {"name": "Riaz Ullah", "student_id": "1208"}, "ricky.benschop@amsterdam.tech": {"name": "Ricky Benschop", "student_id": "1209"}
    # ... (rest of your records)
}

    
  
    
   
    

   







def get_user_details(email):
    """
    Look up the instructor details by email.
    Returns a tuple (name, student_id) if found, or (None, None) if not.
    """
    record = records.get(email)
    if record:
        return record["name"], record["student_id"]
    else:
        return None, None

#*****************************

def read_docx(file_content):
    doc = docx.Document(io.BytesIO(file_content))
    return '\n'.join([para.text for para in doc.paragraphs])

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



def student_dashboard():
    track_activity()
    initialize_session()
    restrict_access(allowed_roles=['student'])

    st.title("Student Dashboard")
    user_email = st.session_state.username
    name1, student_id1 = get_user_details(user_email)
    st.markdown(
        f"<h3 style='font-size:20px;'>Welcome, <span style='color:red;'>{name1}!</span>, your student ID is {student_id1}</h3>",
        unsafe_allow_html=True
    )
    
    st.write("View your assignments and AI-generated feedback.")
    
    student_id_input = st.text_input("Enter your Student ID:")
    if not student_id_input:
        st.warning("Please enter your Student ID to proceed.")
        return
    if not student_id1 == student_id_input:       
        st.warning("Wrong Student ID. Try again.")
        return

    if st.button("Retrieve Assignments"):
        files = search_files_by_student_id(student_id_input)
        unique_files = list(set(files))
        if unique_files:
            st.write(f"Number of files found: {len(unique_files)}")
        else:
            st.warning("No files found for this Student ID.")

    st.header("View AI Feedback")
    conn = get_db_connection()
    cursor = conn.cursor()

    # Course selection
    cursor.execute("""
        SELECT course_id FROM submissions 
        WHERE student_id = %s GROUP BY course_id
    """, (student_id_input,))
    db_courses = [row[0] for row in cursor.fetchall()]
    
    if db_courses:
        courses = ["Nil"] + db_courses
        selected_course = st.selectbox("Select Course", courses, index=0)

    if selected_course != "Nil":
        # Assignment selection
        cursor.execute("""
            SELECT assignment_id, assignment_name 
            FROM submissions 
            WHERE course_id = %s AND student_id = %s 
            GROUP BY assignment_id, assignment_name
        """, (selected_course, student_id_input))
        db_assignments = [f"{a[0]} - {a[1]}" for a in cursor.fetchall()]
        
        if db_assignments:
            assignments = ["Nil - Nil"] + db_assignments
            selected_assignment = st.selectbox("Select Assignment", assignments, index=0)

        if selected_assignment != "Nil - Nil":
            assignment_id, assignment_name = selected_assignment.split(" - ", 1)
            cursor.execute("""
                SELECT DISTINCT file_path 
                FROM submissions 
                WHERE course_id = %s AND assignment_id = %s AND student_id = %s
            """, (selected_course, assignment_id, student_id_input))
            files = cursor.fetchall()
            
            unique_files = list(set([file_info[0] for file_info in files]))
            
            # Slack configuration
            slack_token = os.getenv("SLACK_BOT_TOKEN")
            slack_channel_id = os.getenv("SLACK_CHANNEL_ID")
            instructor_slack_channel = os.getenv("INSTRUCTOR_SLACK_CHANNEL")
            ask_student_channel = os.getenv("ASK_STUDENT_SLACK_CHANNEL")
            
            if unique_files:
                for idx, file_path in enumerate(unique_files):
                    text = ""
                    with st.expander(f"View {file_path.split('/')[-1]}"):
                        blob_client = container_client.get_blob_client(file_path)
                        content = blob_client.download_blob().readall()

                        if file_path.endswith('.docx'):
                            text = read_docx(content)
                            st.text_area("Document Content", text, height=300, 
                                       key=f"text_area_docx_{idx}")
                        elif file_path.endswith('.txt'):
                            text = content.decode()
                            st.text_area("Document Content", text, height=300,
                                       key=f"text_area_txt_{idx}")

                        rubric = fetch_assignment_rubric(assignment_name)

                        if st.button("View Rubric", key=f"view_rubric_{idx}"):
                            st.markdown("""<span style='color:red;'>
                                Click the button at least two times for refined rubric!
                                </span>""", unsafe_allow_html=True)
                            with st.spinner("Converting rubric..."):
                                rubric_table = convert_rubric_to_table(rubric)
                            if rubric_table:
                                st.markdown("### Assignment Rubric")
                                st.markdown(rubric_table, unsafe_allow_html=True)
                            else:
                                st.error("Could not generate rubric table")
                                       
                        if st.button(f"Generate AI Feedback", key=f"ai_feedback_{file_path}_{idx}"):
                            st.markdown("""<span style='color:red;'>
                                Click multiple times for new perspectives!
                                </span>""", unsafe_allow_html=True)
                            with st.spinner("Generating feedback..."):
                                result = get_ai_feedback_student(rubric, text)
                                if "error" in result:
                                    st.error(f"AI Error: {result['error']}")
                                else:
                                    st.session_state[f"feedback_{file_path}"] = result['feedback']
                                    st.session_state[f"suggestions_{file_path}"] = result['suggestions']
                                    
                        if f"feedback_{file_path}" in st.session_state:
                            feedback = st.session_state[f"feedback_{file_path}"]
                            suggestions = st.session_state[f"suggestions_{file_path}"]
                            
                            st.subheader("Review AI Grading")
                            st.code(feedback, language=None)
                            st.code(suggestions, language=None)

                            headers = {
                                "Content-Type": "application/json; charset=utf-8",
                                "Authorization": f"Bearer {slack_token}"
                            }

                            # Slack integration buttons
                            if st.button("Send to Slack", key=f"send_slack_{file_path}_{idx}"):
                                message = f"""*Feedback for {file_path.split('/')[-1]}*:\n
                                    *Feedback:*\n{feedback}\n
                                    *Suggestions:*\n{suggestions}"""
                                payload = {"channel": slack_channel_id, "text": message}
                                response = requests.post("https://slack.com/api/chat.postMessage", 
                                                       headers=headers, data=json.dumps(payload))
                                if response.ok:
                                    st.success("Sent to Slack!")
                                else:
                                    st.error("Failed to send")

                            mentor_guidance = st.radio(
                                "**Need Clarification?**", 
                                ("Yes", "No"), 
                                key=f"mentor_{file_path}_{idx}"
                            )
                           
                            comment = ""
                            if mentor_guidance == "Yes":
                                comment = st.text_area(
                                    "Comment for Mentors:", 
                                    key=f"comment_{file_path}_{idx}"
                                )
                                if st.button("Ask Instructor", key=f"ask_instructor_{file_path}_{idx}"):
                                    instructor_msg = f"Student {student_id_input}: {comment}"
                                    payload = {"channel": instructor_slack_channel, "text": instructor_msg}
                                    response = requests.post("https://slack.com/api/chat.postMessage", 
                                                           headers=headers, data=json.dumps(payload))
                                    if response.ok:
                                        st.success("Sent to instructor!")
                                    else:
                                        st.error("Failed to send")

                            if st.button("Ask Peers", key=f"ask_peers_{file_path}_{idx}"):
                                peer_msg = f"Student {student_id_input} needs help with {file_path.split('/')[-1]}"
                                payload = {"channel": ask_student_channel, "text": peer_msg}
                                response = requests.post("https://slack.com/api/chat.postMessage", 
                                                       headers=headers, data=json.dumps(payload))
                                if response.ok:
                                    st.success("Request sent to peers!")
                                else:
                                    st.error("Failed to send")

                            # New Approve & Save button
                            if st.button("✅ Approve & Save", key=f"approve_{file_path}_{idx}"):
                                record = {
                                    "course_id": selected_course,
                                    "assignment": assignment_name,
                                    "student": student_id_input,
                                    "file": file_path,
                                    "feedback": feedback,
                                    "suggestions": suggestions,
                                    "need_more_clarity_comment": comment,
                                    "timestamp": pd.Timestamp.now().isoformat()
                                }

                                save_result = save_grading_record_student(record)
                                
                                if save_result == 'success':
                                    st.success("Feedback saved successfully!")
                                    st.markdown("""
                                        <script>
                                        setTimeout(function(){
                                            var elements = document.querySelectorAll('.stAlert');
                                            elements[elements.length-1].style.display='none';
                                        }, 2000);
                                        </script>
                                    """, unsafe_allow_html=True)
                                elif save_result == 'duplicate':
                                    st.error("Duplicate entry - already saved!")
                                    st.markdown("""
                                        <script>
                                        setTimeout(function(){
                                            var elements = document.querySelectorAll('.stAlert');
                                            elements[elements.length-1].style.display='none';
                                        }, 2000);
                                        </script>
                                    """, unsafe_allow_html=True)
                                else:
                                    st.error("Error saving feedback")

    # Preview and Export Section
    st.markdown("---")
    st.subheader("Preview & Export Feedback")
    
    time_filter = st.selectbox(
        "Select Time Range",
        options=['last_hour', 'last_day', 'last_week', 'last_month', 'last_year', 'all_time'],
        format_func=lambda x: x.replace('_', ' ').title(),
        key='time_filter'
    )

    if st.button("Preview Feedback"):
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                intervals = {
                    'last_hour': '1 HOUR',
                    'last_day': '1 DAY',
                    'last_week': '1 WEEK',
                    'last_month': '1 MONTH',
                    'last_year': '1 YEAR',
                    'all_time': '100 YEAR'
                }
                cursor.execute("""
                    SELECT course_id, assignment, student, file, feedback, suggestions,
                           need_more_clarity_comment, timestamp 
                    FROM student_grading_records
                    WHERE student = %s AND timestamp >= NOW() - INTERVAL %s
                    ORDER BY timestamp DESC
                """, (student_id_input, intervals[time_filter]))
                
                data = cursor.fetchall()
                if data:
                    df = pd.DataFrame(data, columns=[
                        "Course", "Assignment", "student", "File", "Feedback", 
                        "Suggestions", "Clarification Request", "Timestamp"
                    ])
                    st.dataframe(df.style.set_properties(**{
                        'text-align': 'left',
                        'white-space': 'pre-wrap'
                    }))
                else:
                    st.warning("No saved feedback found")
        except Exception as e:
            st.error(f"Database error: {str(e)}")
        finally:
            conn.close()

    if st.button("Export to Excel"):
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT * FROM student_grading_records
                    WHERE student = %s
                    ORDER BY timestamp DESC
                """, (student_id_input,))
                
                data = cursor.fetchall()
                if data:
                    df = pd.DataFrame(data, columns=[
                        "id", "course_id", "assignment", "student", "file",
                         "feedback", "suggestions",
                        "need_more_clarity_comment", "timestamp"
                    ])
                    
                    output = io.BytesIO()
                    with pd.ExcelWriter(output, engine='openpyxl') as writer:
                        df.to_excel(writer, index=False)
                    
                    st.download_button(
                        label="📥 Download Excel",
                        data=output.getvalue(),
                        file_name=f"student_feedback_{time_filter}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
                else:
                    st.warning("No data to export")
        except Exception as e:
            st.error(f"Database error: {str(e)}")
        finally:
            conn.close()

if __name__ == "__main__":
    student_dashboard()
    
    
    
    
    
# def student_dashboard():
#     track_activity()
#     initialize_session()
#     restrict_access(allowed_roles=['student'])

#     st.title("Student Dashboard")
#     user_email = st.session_state.username
#     name1, student_id1 = get_user_details(user_email)
#     st.markdown(
#         f"<h3 style='font-size:20px;'>Welcome,   <span style='color:red;'>{name1}!</span>, your student ID is {student_id1} </h3>",
#         unsafe_allow_html=True
#     )
    
#     st.write("View your assignments and AI-generated feedback.")
    
#     student_id_input = st.text_input("Enter your Student ID:")
#     if not student_id_input:
#         st.warning("Please enter your Student ID to proceed.")
#         return
#     if not student_id1 == student_id_input:       
#          st.warning("Wrong Student ID. Try again.")
      
#     else:
#         if st.button("Fetch Assignments"):
#             files = search_files_by_student_id(student_id_input)
#             unique_files = list(set(files))
#             if unique_files:
#                 st.write(f"Number of files found: {len(unique_files)}")
#             else:
#                 st.warning("No files found for this Student ID.")

#         st.header("View AI Feedback")
#         conn = get_db_connection()
#         cursor = conn.cursor()

#         # Only fetch courses if student has submissions
#         cursor.execute("""
#             SELECT course_id 
#             FROM submissions 
#             WHERE student_id = %s 
#             GROUP BY course_id
#         """, (student_id_input,))
#         db_courses = [row[0] for row in cursor.fetchall()]
        
#         if db_courses:
#             # Initialize with Nil default
#             courses = ["Nil"]
#             courses = ["Nil"] + db_courses
#             selected_course = st.selectbox("Select Course", courses, index=0)

#         if selected_course != "Nil":
#             # Initialize assignments with Nil default
#             # assignments = ["Nil - Nil"]
#             # Fetch actual assignments if course is selected
#             cursor.execute("""
#                 SELECT assignment_id, assignment_name 
#                 FROM submissions 
#                 WHERE course_id = %s AND student_id = %s 
#                 GROUP BY assignment_id, assignment_name
#             """, (selected_course, student_id_input))
#             db_assignments = [f"{a[0]} - {a[1]}" for a in cursor.fetchall()]
            
#             if db_assignments:
#                 assignments = ["Nil - Nil"]
#                 assignments = ["Nil - Nil"] + db_assignments
#                 selected_assignment = st.selectbox(
#                     "Select Assignment",
#                     assignments,
#                     index=0
#                 )

#             if selected_assignment != "Nil - Nil":
#                 assignment_id, assignment_name = selected_assignment.split(" - ", 1)
#                 cursor.execute("""
#                     SELECT DISTINCT file_path 
#                     FROM submissions 
#                     WHERE course_id = %s AND assignment_id = %s AND student_id = %s
#                 """, (selected_course, assignment_id, student_id_input))
#                 files = cursor.fetchall()
                
#                 unique_files = list(set([file_info[0] for file_info in files]))
                
#                 # Slack configuration
#                 slack_token = os.getenv("SLACK_BOT_TOKEN")
#                 slack_channel_id = os.getenv("SLACK_CHANNEL_ID")
#                 instructor_slack_channel = os.getenv("INSTRUCTOR_SLACK_CHANNEL")
#                 ask_student_channel = os.getenv("ASK_STUDENT_SLACK_CHANNEL")
                
#                 if unique_files:
#                     for idx, file_path in enumerate(unique_files):
#                         text = ""
#                         with st.expander(f"View {file_path.split('/')[-1]}"):
#                             blob_client = container_client.get_blob_client(file_path)
#                             content = blob_client.download_blob().readall()

#                             if file_path.endswith('.docx'):
#                                 text = read_docx(content)
#                                 st.text_area("Document Content", text, height=300, key=f"text_area_docx_{idx}")
#                             elif file_path.endswith('.txt'):
#                                 text = content.decode()
#                                 st.text_area("Document Content", text, height=300, key=f"text_area_txt_{idx}")

#                             rubric = fetch_assignment_rubric(assignment_name)

#                             if st.button("View Rubric", key=f"view_rubric_{idx}"):
#                                 st.markdown(
#                                     "<span style='color:red;'>Click the button at least two times, and each click will prompt the AI to refined rubric table!</span>",
#                                      unsafe_allow_html=True)
#                                 with st.spinner("Converting rubric to table..."):
#                                     rubric_table = convert_rubric_to_table(rubric)
            
#                                 if rubric_table:
#                                     st.markdown("### Assignment Rubric")
#                                     st.markdown(rubric_table, unsafe_allow_html=True)
#                                 else:
#                                     st.error("Could not generate rubric table")
                                               
#                             if st.button(f"Generate AI Feedback", key=f"ai_feedback_{file_path}_{idx}"):
#                                 st.markdown(
#                                     "<span style='color:red;'>Click the button at least three times, and each click will prompt the AI to offer a new phrasing and refined perspective!</span>",
#                                      unsafe_allow_html=True)

#                                 with st.spinner("Generating feedback..."):
#                                     result = get_ai_feedback_student(rubric, text)
                                       
#                                     if "error" in result:
#                                         st.error(f"AI Error: {result['error']}")
#                                     else:
#                                         st.session_state[f"feedback_{file_path}"] = result['feedback']
#                                         st.session_state[f"suggestions_{file_path}"] = result['suggestions']
                                        
                                        
#                             if f"feedback_{file_path}" in st.session_state:
#                                 # ... rest of the feedback handling code remains the same ...
#                                     # Retrieve the feedback and suggestions from session state
#                                     feedback = st.session_state[f"feedback_{file_path}"]
#                                     suggestions = st.session_state[f"suggestions_{file_path}"]
                                    
#                                     st.subheader("Review AI Grading")
#                                     st.code(feedback, language=None)
#                                     st.code(suggestions, language=None)
    
#                                     headers = {
#                                             "Content-Type": "application/json; charset=utf-8",
#                                             "Authorization": f"Bearer {slack_token}"
#                                         }
    
    
#                                     if st.button("Send feedback to my Slack Channel", key=f"send_slack_{file_path}_{idx}"):
#                                         message = (
#                                             f"*Feedback for {file_path.split('/')[-1]}*:\n\n"
#                                             f"*Feedback:*\n{feedback}\n\n"
#                                             f"*Suggestions:*\n{suggestions}"
#                                         )
#                                     # headers = {
#                                     #     "Content-Type": "application/json; charset=utf-8",
#                                     #     "Authorization": f"Bearer {slack_token}"
#                                     # }
#                                         payload = {"channel": slack_channel_id, "text": message}
#                                         response = requests.post("https://slack.com/api/chat.postMessage", 
#                                                                headers=headers, 
#                                                                data=json.dumps(payload))
#                                         if response.status_code == 200:
#                                             st.success(f"Message sent to channel {slack_channel_id} successfully!")
#                                         else:
#                                             st.error(f"Failed to send message. Reason: {response.text}")

#                                     if st.button("Accept Feedback", key=f"accept_{idx}"):
#                                         if save_feedback_to_db(
#                                             student_id=student_id_input,
#                                             course_id=selected_course,
#                                             assignment_id=assignment_id,
#                                             file_path=file_path,
#                                             feedback=feedback,  # using local variable
#                                             suggestions=suggestions
#                                             # feedback=st.session_state[f"feedback_{file_path}_{idx}"],
#                                             # suggestions=st.session_state[f"suggestions_{file_path}_{idx}"]
#                                         ):
#                                             st.success("Feedback saved to database!")
#                                         else:
#                                             st.error("Error saving feedback")

#                                     # st.markdown("<h5 style='color:red;'>NEED MORE CLARITY:</h5>", unsafe_allow_html=True)
                          
 
#                                     mentor_guidance = st.radio(
#                                         "**NEED MORE CLARITY**: Do you need mentor guidance based on the feedback?", 
#                                         ("Yes", "No"), 
#                                         key=f"mentor_option_{file_path}_{idx}"
#                                     )
                               
#                                     if mentor_guidance == "Yes":
#                                         comment = st.text_area(
#                                             "Kindly enter a comment to be shared in the Mentors channel:", 
#                                             key=f"comment_{file_path}_{idx}"
#                                         )
#                                         if st.button("Send to Instructor", key=f"send_instructor_{file_path}_{idx}"):
#                                             instructor_message = f"Student {student_id_input} comment: {comment}"
#                                             payload = {"channel": instructor_slack_channel, "text": instructor_message}
#                                             response = requests.post("https://slack.com/api/chat.postMessage", 
#                                                                    headers=headers, 
#                                                                    data=json.dumps(payload))
#                                             if response.status_code == 200:
#                                                 st.success("Comment sent to instructor!")
#                                             else:
#                                                 st.error("Failed to send comment.")
   
#                                     if st.button("Ask Peers for Help", key=f"ask_student_{file_path}_{idx}"):
#                                         student_message = f"Student {student_id_input} needs help with {file_path.split('/')[-1]}"
#                                         payload = {"channel": ask_student_channel, "text": student_message}
#                                         response = requests.post("https://slack.com/api/chat.postMessage", 
#                                                                headers=headers, 
#                                                                data=json.dumps(payload))
#                                         if response.status_code == 200:
#                                             st.success("Request sent to peers!")
#                                         else:
#                                             st.error("Failed to send request.")
                                        
#                     # else:
#                         # st.warning("No files found for this assignment.")                                
#                 else:
#                     st.warning("No files found for this assignment.")
#             else:
#                 if selected_assignment == "Nil - Nil":
#                     st.info("Please select an assignment")
#         else:
#             if selected_course == "Nil":
#                 st.info("Please select a course")
                
#         # Add Preview and Export section
#         st.markdown("---")
#         st.subheader("Preview and Export Feedback")
        
#         # Time filter selection
#         time_filter = st.selectbox(
#             "Select Time Range",
#             options=['last_hour', 'last_day', 'last_week', 'last_month', 'last_year', 'all_time'],
#             format_func=lambda x: x.replace('_', ' ').title(),
#             key='student_time_filter'
#         )

#         col1, col2 = st.columns(2)
#         with col1:
#             if st.button("Preview My Feedback"):
#                 feedback_records = get_accepted_feedback(student_id_input, time_filter)
#                 if not feedback_records.empty:
#                     st.dataframe(feedback_records)
#                 else:
#                     st.warning("No feedback records found")

#         with col2:
#             if st.button("Export to Excel"):
#                 feedback_records = get_accepted_feedback(student_id_input, time_filter)
#                 if not feedback_records.empty:
#                     output = io.BytesIO()
#                     with pd.ExcelWriter(output, engine='openpyxl') as writer:
#                         feedback_records.to_excel(writer, index=False)
#                     st.download_button(
#                         label="Download Excel File",
#                         data=output.getvalue(),
#                         file_name=f"my_feedback_{time_filter}.xlsx",
#                         mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
#                     )
#                 else:
#                     st.warning("No records to export")        

# if __name__ == "__main__":
#     student_dashboard()





