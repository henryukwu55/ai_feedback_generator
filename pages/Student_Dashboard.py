import streamlit as st
import pandas as pd
import requests
import json
import os
import io
from utils.session import initialize_session, restrict_access, update_activity
from utils.canvas_integration import search_files_by_student_id, read_docx, read_pdf, read_md, read_pages, parse_pages_xml, search_files_by_student_id, get_user_details, parse_pages_xml
from database.connection import get_db_connection
from utils.grading import fetch_assignment_rubric, get_ai_feedback_student, convert_rubric_to_table, save_grading_record_student, format_text_for_display
from utils.azure_storage import *
from database.operations import fetch_student_assignments, save_feedback_to_db, get_accepted_feedback
from dotenv import load_dotenv

load_dotenv()

import streamlit as st

# Remove ONLY the "About" option from the menu
hide_about_option = """
<style>
/* Hide the About menu item */
li[data-testid="main-menu-about"] {
    display: none !important;
}
</style>
"""
st.markdown(hide_about_option, unsafe_allow_html=True)



def track_activity():
    if st.session_state.get("logged_in"):
        update_activity()

current_theme = st.get_option("theme.base")
if current_theme == "dark":
    st.markdown("""
        <style>
            [data-testid="stTextArea"] textarea,
            [data-testid="stTextInput"] input,
            [data-testid="stNumberInput"] input {
                background-color: #2D2D2D !important;
                color: #FFFFFF !important;
                border: 1px solid #555555 !important;
            }
            .stTextArea textarea:focus {
                border-color: #4A90E2 !important;
                box-shadow: 0 0 0 0.2rem rgba(74, 144, 226, 0.25) !important;
            }
        </style>
    """, unsafe_allow_html=True)

st.markdown("""
    <style>
    .stButton>button {
        background-color: grey !important;
        color: white !important;
        transition: all 0.3s ease !important;
    }
    .stButton>button:hover { opacity: 0.8 !important; transform: scale(1.05) !important; }
    [data-testid="expander"] > div:first-child {
        background-color: grey !important;
        color: white !important;
        border-radius: 8px !important;
    }
    </style>
""", unsafe_allow_html=True)



#*****************************
# Full data stored as a dictionary of dictionaries
records = {
    "jozsef.dudas@elu.nl": {"name": "Dudás József", "student_id": "403"}, "leon.aziz@elu.nl": {"name": "Leon Aziz", "student_id": "182"},
    "yana.kondratyuk@elu.nl": {"name": "Yana Kondratyuk", "student_id": "165"}, "erika.parra@elu.nl": {"name": "Erika Parra", "student_id": "464"},
    "viktor.rodau@elu.nl": {"name": "Viktor Rodau", "student_id": "181"}, "moisieiev.mykyta@elu.nl": {"name": "Moisieiev Mykyta", "student_id": "139"},
    "george.vilnoiu@elu.nl": {"name": "George Vilnoiu", "student_id": "153"}, "test_student@amsterdam.tech": {"name": "Test Student", "student_id": "464"},
    "ify@amsterdam.tech": {"name": "Ify Genevieve", "student_id": "464"}, "naz.aydin@amsterdam.tech": {"name": "Naz Aydin", "student_id": "1214"},
    "riaz.ullah@amsterdam.tech": {"name": "Riaz Ullah", "student_id": "1208"}, "ricky.benschop@amsterdam.tech": {"name": "Ricky Benschop", "student_id": "1209"},
    "isadora@amsterdam.tech": {"name": "Isadora Costa", "student_id": "2655"}, "henry@amsterdam.tech": {"name": "Henry Ukwu", "student_id": "1561"}
    
}



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
    
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
    
    student_id_input = st.text_input("Enter your Student ID:")
    if not student_id_input:
        st.warning("Please enter your Student ID to proceed.")
        return
    if not student_id1 == student_id_input:       
        st.warning("Wrong Student ID. Try again.")
        return

    if st.button("Retrieve assignments"):
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
    cursor.execute("SELECT DISTINCT course_id FROM submissions WHERE student_id = %s", (student_id_input,))
    db_courses = [row[0] for row in cursor.fetchall()]
    courses = ["Nil"] + db_courses
    selected_course = st.selectbox("Select Course", courses, index=0)

    if selected_course != "Nil":
        cursor.execute("""
            SELECT assignment_id, assignment_name 
            FROM submissions 
            WHERE course_id = %s AND student_id = %s 
            GROUP BY assignment_id, assignment_name
        """, (selected_course, student_id_input))
        db_assignments = [f"{a[0]} - {a[1]}" for a in cursor.fetchall()]
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
            slack_token = os.getenv("SLACK_BOT_TOKEN")
            slack_channel_id = os.getenv("SLACK_CHANNEL_ID")
            instructor_slack_channel = os.getenv("INSTRUCTOR_SLACK_CHANNEL")
            ask_student_channel = os.getenv("ASK_STUDENT_SLACK_CHANNEL")

            # Define a list of rotating messages           
            rotating_messages = [
                   "You have done an excellent job!",
                   "Great job!",
                   "Nice work! Keep pushing your thinking.",
                   "Impressive effort!",
                   "Well done! You're on the right track.",
                   "Fantastic work—your progress is clear!",
                   "You're doing really well, keep up the momentum!",
                   "Solid work!",
                   "Keep going—you’re making strong progress.",
                   "Outstanding commitment to quality!",
                   "You’re building a strong foundation. Keep it up!",
                   "Nice job! You’re thinking like a problem solver.",
                   "Very thoughtful work. Keep refining your ideas.",
                   "Bravo! Your work reflects your dedication."
            ]
    
            # Initialize message index in session state if not already
            if "message_index" not in st.session_state:
                st.session_state["message_index"] = 0
            # Get the current message
            current_message = rotating_messages[st.session_state["message_index"]]

            # Define a function to increment the index
            def cycle_message():
                st.session_state["message_index"] = (st.session_state["message_index"] + 1) % len(rotating_messages)


            if unique_files:
                for idx, file_path in enumerate(unique_files):
                    with st.expander(f"View {os.path.basename(file_path)}"):
                        blob_client = container_client.get_blob_client(file_path)
                        content = blob_client.download_blob().readall()

                        if len(content) > MAX_FILE_SIZE:
                            st.error(f"File too large to process ({len(content)/1024/1024:.1f}MB)")
                            continue

                        formatted_key = f"formatted_{file_path}"
                        if formatted_key not in st.session_state:
                            st.session_state[formatted_key] = None

                        # File type handling
                        if file_path.endswith('.docx'):
                            text = read_docx(content)
                        elif file_path.endswith('.pdf'):
                            text = read_pdf(content)
                        elif file_path.endswith('.md'):
                            text = read_md(content)
                        elif file_path.endswith('.pages'):
                            text = read_pages(content)
                        elif file_path.endswith('.txt'):
                            text = content.decode('utf-8')
                        else:
                            text = f"Unsupported file format: {file_path.split('.')[-1]}"

                        # Formatting controls
                        col1, col2 = st.columns([3, 1])
                        with col1:
                            if st.button("🖋️ View Formatted Document", 
                                       key=f"format_{file_path}_{idx}",
                                       help="Enhance document formatting"):
                                with st.spinner("Formatting..."):
                                    st.session_state[formatted_key] = format_text_for_display(text)
                        
                        with col2:
                            if st.session_state[formatted_key]:
                                if st.button("❌ Clear Formatting", 
                                           key=f"clear_{file_path}_{idx}"):
                                    st.session_state[formatted_key] = None

                        # Display content
                        if st.session_state[formatted_key]:
                            st.text_area("Formatted Content", 
                                       st.session_state[formatted_key], 
                                       height=400,
                                       key=f"formatted_area_{idx}")
                        else:
                            st.text_area("Document Content", 
                                       text, 
                                       height=400,
                                       key=f"raw_area_{idx}")

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
                                       
                        if st.button(f"Generate AI Feedback", key=f"ai_feedback_{file_path}_{idx}", on_click=cycle_message):
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
                            
                            # Check if either feedback or suggestions is non-empty and non-null
                            has_feedback = feedback is not None and feedback.strip() != ""
                            has_suggestions = suggestions is not None and suggestions.strip() != ""
                            
                            if has_feedback or has_suggestions:
                            
                              st.subheader("View AI Feedback & Reflection Points")
                              if has_feedback:
                                st.code(feedback, language=None)
                         
                              # Show rotating markdown message
                              current_message = rotating_messages[st.session_state["message_index"]]
                            
                              st.markdown(
                                f"<span style='color:blue;'>{current_message} Reflect on these major points to deepen your understanding and further enhance your work.</span>",
                                   unsafe_allow_html=True
                               )
                                          
                              if has_suggestions:
                                st.code(suggestions, language=None)
                            
                              st.markdown(
                                 f"<span style='color:purple; font-size:11px; font-style:italic; font-weight:bold;'>"
                                 f"Note: This is AI-assisted guidance. Verify critical suggestions with your instructor."
                                 f"</span>",
                                     unsafe_allow_html=True
                               )

                            #   st.markdown(
                            #     f"_<span style='color:purple;font-size:9px;'> <b>Note<b>: This is AI-assisted guidance. Verify critical suggestions with your instructor._</span>",
                            #        unsafe_allow_html=True
                            #    )
                            else:
                               st.info("No AI feedback or suggestions available for this file yet.")
                                  
                            headers = {
                                "Content-Type": "application/json; charset=utf-8",
                                "Authorization": f"Bearer {slack_token}"
                            }

                            if st.button("Send to my slack channel", key=f"send_slack_{file_path}_{idx}"):
                                message = f"""*Feedback for {file_path.split('/')[-1]}*:\n
                                    *Feedback:*\n{feedback}\n
                                    *Suggestions:* \n{suggestions}"""
                                payload = {"channel": slack_channel_id, "text": message}
                                response = requests.post("https://slack.com/api/chat.postMessage", 
                                                       headers=headers, data=json.dumps(payload))
                                if response.ok:
                                    st.success("Sent to Slack!")
                                else:
                                    st.error("Failed to send")

                            # Mandatory clarification section
                            mentor_guidance = st.radio(
                                "**Need More Clarification?** (Required)",
                                ("Yes", "No"),
                                key=f"mentor_{file_path}_{idx}",
                                index=None  # No default selection
                            )
                           
                            comment = ""
                            if mentor_guidance == "Yes":
                                comment = st.text_area(
                                    "Comment for Mentors (Required):", 
                                    key=f"comment_{file_path}_{idx}"
                                )
                            elif mentor_guidance is None:
                                st.error("To proceed, You must select Yes or No for clarification needs")

                            if st.button("Ask Peers for Assistance", key=f"ask_peers_{file_path}_{idx}"):
                                peer_msg = f"{name1}, Student ID: {student_id_input} needs help with {file_path.split('/')[-1]} \n\n Assistance Focus: \n{suggestions}"
                                payload = {"channel": ask_student_channel, "text": peer_msg}
                                response = requests.post("https://slack.com/api/chat.postMessage", 
                                                       headers=headers, data=json.dumps(payload)) 
                                if response.ok:
                                    st.success("Request sent to peers!")
                                else:
                                    st.error("Failed to send")

                            if st.button("✅ Approve & Save Feedback", key=f"approve_{file_path}_{idx}"):
                                # Validation checks
                                validation_passed = True
                                
                                if mentor_guidance is None:
                                    st.error("You must select Yes or No for clarification needs")
                                    validation_passed = False
                                    
                                if mentor_guidance == "Yes" and not comment.strip():
                                    st.error("You must provide a comment when selecting 'Yes'")
                                    validation_passed = False
                                
                                if validation_passed:
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
#         f"<h3 style='font-size:20px;'>Welcome, <span style='color:red;'>{name1}!</span>, your student ID is {student_id1}</h3>",
#         unsafe_allow_html=True
#     )
    
#     MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
    
#     student_id_input = st.text_input("Enter your Student ID:")
#     if not student_id_input:
#         st.warning("Please enter your Student ID to proceed.")
#         return
#     if not student_id1 == student_id_input:       
#         st.warning("Wrong Student ID. Try again.")
#         return

#     if st.button("Retrieve assignments"):
#         files = search_files_by_student_id(student_id_input)
#         unique_files = list(set(files))
#         if unique_files:
#             st.write(f"Number of files found: {len(unique_files)}")
#         else:
#             st.warning("No files found for this Student ID.")

#     st.header("View AI Feedback")
#     conn = get_db_connection()
#     cursor = conn.cursor()
    
#     # Course selection
#     cursor.execute("SELECT DISTINCT course_id FROM submissions WHERE student_id = %s", (student_id_input,))
#     db_courses = [row[0] for row in cursor.fetchall()]
#     courses = ["Nil"] + db_courses
#     selected_course = st.selectbox("Select Course", courses, index=0)

#     if selected_course != "Nil":
#         cursor.execute("""
#             SELECT assignment_id, assignment_name 
#             FROM submissions 
#             WHERE course_id = %s AND student_id = %s 
#             GROUP BY assignment_id, assignment_name
#         """, (selected_course, student_id_input))
#         db_assignments = [f"{a[0]} - {a[1]}" for a in cursor.fetchall()]
#         assignments = ["Nil - Nil"] + db_assignments
#         selected_assignment = st.selectbox("Select Assignment", assignments, index=0)

#         if selected_assignment != "Nil - Nil":
#             assignment_id, assignment_name = selected_assignment.split(" - ", 1)
#             cursor.execute("""
#                 SELECT DISTINCT file_path 
#                 FROM submissions 
#                 WHERE course_id = %s AND assignment_id = %s AND student_id = %s
#             """, (selected_course, assignment_id, student_id_input))
#             files = cursor.fetchall()
            
#             unique_files = list(set([file_info[0] for file_info in files]))
#             slack_token = os.getenv("SLACK_BOT_TOKEN")
#             slack_channel_id = os.getenv("SLACK_CHANNEL_ID")
#             instructor_slack_channel = os.getenv("INSTRUCTOR_SLACK_CHANNEL")
#             ask_student_channel = os.getenv("ASK_STUDENT_SLACK_CHANNEL")

#             if unique_files:
#                 for idx, file_path in enumerate(unique_files):
#                     with st.expander(f"View {os.path.basename(file_path)}"):
#                         blob_client = container_client.get_blob_client(file_path)
#                         content = blob_client.download_blob().readall()

#                         if len(content) > MAX_FILE_SIZE:
#                             st.error(f"File too large to process ({len(content)/1024/1024:.1f}MB)")
#                             continue

#                         formatted_key = f"formatted_{file_path}"
#                         if formatted_key not in st.session_state:
#                             st.session_state[formatted_key] = None

#                         # File type handling
#                         if file_path.endswith('.docx'):
#                             text = read_docx(content)
#                         elif file_path.endswith('.pdf'):
#                             text = read_pdf(content)
#                         elif file_path.endswith('.md'):
#                             text = read_md(content)
#                         elif file_path.endswith('.pages'):
#                             text = read_pages(content)
#                         elif file_path.endswith('.txt'):
#                             text = content.decode('utf-8')
#                         else:
#                             text = f"Unsupported file format: {file_path.split('.')[-1]}"

#                         # Formatting controls
#                         col1, col2 = st.columns([3, 1])
#                         with col1:
#                             if st.button("🖋️ View Formatted Document", 
#                                        key=f"format_{file_path}_{idx}",
#                                        help="Enhance document formatting"):
#                                 with st.spinner("Formatting..."):
#                                     st.session_state[formatted_key] = format_text_for_display(text)
                        
#                         with col2:
#                             if st.session_state[formatted_key]:
#                                 if st.button("❌ Clear Formatting", 
#                                            key=f"clear_{file_path}_{idx}"):
#                                     st.session_state[formatted_key] = None

#                         # Display content
#                         if st.session_state[formatted_key]:
#                             st.text_area("Formatted Content", 
#                                        st.session_state[formatted_key], 
#                                        height=400,
#                                        key=f"formatted_area_{idx}")
#                         else:
#                             st.text_area("Document Content", 
#                                        text, 
#                                        height=400,
#                                        key=f"raw_area_{idx}")

#                         rubric = fetch_assignment_rubric(assignment_name)

#                         if st.button("View Rubric", key=f"view_rubric_{idx}"):
#                             st.markdown("""<span style='color:red;'>
#                                 Click the button at least two times for refined rubric!
#                                 </span>""", unsafe_allow_html=True)
#                             with st.spinner("Converting rubric..."):
#                                 rubric_table = convert_rubric_to_table(rubric)
#                             if rubric_table:
#                                 st.markdown("### Assignment Rubric")
#                                 st.markdown(rubric_table, unsafe_allow_html=True)
#                             else:
#                                 st.error("Could not generate rubric table")
                                       
#                         if st.button(f"Generate AI Feedback", key=f"ai_feedback_{file_path}_{idx}"):
#                             st.markdown("""<span style='color:red;'>
#                                 Click multiple times for new perspectives!
#                                 </span>""", unsafe_allow_html=True)
#                             with st.spinner("Generating feedback..."):
#                                 result = get_ai_feedback_student(rubric, text)
#                                 if "error" in result:
#                                     st.error(f"AI Error: {result['error']}")
#                                 else:
#                                     st.session_state[f"feedback_{file_path}"] = result['feedback']
#                                     st.session_state[f"suggestions_{file_path}"] = result['suggestions']
                                    
#                         if f"feedback_{file_path}" in st.session_state:
#                             feedback = st.session_state[f"feedback_{file_path}"]
#                             suggestions = st.session_state[f"suggestions_{file_path}"]
                            
#                             st.subheader("Review AI Grading")
#                             st.code(feedback, language=None)
#                             st.code(suggestions, language=None)

#                             headers = {
#                                 "Content-Type": "application/json; charset=utf-8",
#                                 "Authorization": f"Bearer {slack_token}"
#                             }

#                             if st.button("Send to my slack channel", key=f"send_slack_{file_path}_{idx}"):
#                                 message = f"""*Feedback for {file_path.split('/')[-1]}*:\n
#                                     *Feedback:*\n{feedback}\n
#                                     *Suggestions:*\n{suggestions}"""
#                                 payload = {"channel": slack_channel_id, "text": message}
#                                 response = requests.post("https://slack.com/api/chat.postMessage", 
#                                                        headers=headers, data=json.dumps(payload))
#                                 if response.ok:
#                                     st.success("Sent to Slack!")
#                                 else:
#                                     st.error("Failed to send")

#                             mentor_guidance = st.radio(
#                                 "**Need Clarification?**", 
#                                 ("Yes", "No"), 
#                                 key=f"mentor_{file_path}_{idx}"
#                             )
                           
#                             comment = ""
#                             if mentor_guidance == "Yes":
#                                 comment = st.text_area(
#                                     "Comment for Mentors:", 
#                                     key=f"comment_{file_path}_{idx}"
#                                 )
#                                 if st.button("Ask Instructor", key=f"ask_instructor_{file_path}_{idx}"):
#                                     instructor_msg = f"Message from {name1}, Student ID: {student_id_input}: {comment}"
#                                     payload = {"channel": instructor_slack_channel, "text": instructor_msg}
#                                     response = requests.post("https://slack.com/api/chat.postMessage", 
#                                                            headers=headers, data=json.dumps(payload))
#                                     if response.ok:
#                                         st.success("Sent to instructor!")
#                                     else:
#                                         st.error("Failed to send")

#                             if st.button("Ask Peers", key=f"ask_peers_{file_path}_{idx}"):
#                                 peer_msg = f"{name1}, Student ID: {student_id_input} needs help with {file_path.split('/')[-1]} \n\n Assistance Focus: \n{suggestions}"
#                                 payload = {"channel": ask_student_channel, "text": peer_msg}
#                                 response = requests.post("https://slack.com/api/chat.postMessage", 
#                                                        headers=headers, data=json.dumps(payload)) 
#                                 if response.ok:
#                                     st.success("Request sent to peers!")
#                                 else:
#                                     st.error("Failed to send")

#                             if st.button("✅ Approve & Save", key=f"approve_{file_path}_{idx}"):
#                                 record = {
#                                     "course_id": selected_course,
#                                     "assignment": assignment_name,
#                                     "student": student_id_input,
#                                     "file": file_path,
#                                     "feedback": feedback,
#                                     "suggestions": suggestions,
#                                     "need_more_clarity_comment": comment,
#                                     "timestamp": pd.Timestamp.now().isoformat()
#                                 }

#                                 save_result = save_grading_record_student(record)
                                
#                                 if save_result == 'success':
#                                     st.success("Feedback saved successfully!")
#                                     st.markdown("""
#                                         <script>
#                                         setTimeout(function(){
#                                             var elements = document.querySelectorAll('.stAlert');
#                                             elements[elements.length-1].style.display='none';
#                                         }, 2000);
#                                         </script>
#                                     """, unsafe_allow_html=True)
#                                 elif save_result == 'duplicate':
#                                     st.error("Duplicate entry - already saved!")
#                                     st.markdown("""
#                                         <script>
#                                         setTimeout(function(){
#                                             var elements = document.querySelectorAll('.stAlert');
#                                             elements[elements.length-1].style.display='none';
#                                         }, 2000);
#                                         </script>
#                                     """, unsafe_allow_html=True)
#                                 else:
#                                     st.error("Error saving feedback")

#     # Preview and Export Section
#     st.markdown("---")
#     st.subheader("Preview & Export Feedback")
    
#     time_filter = st.selectbox(
#         "Select Time Range",
#         options=['last_hour', 'last_day', 'last_week', 'last_month', 'last_year', 'all_time'],
#         format_func=lambda x: x.replace('_', ' ').title(),
#         key='time_filter'
#     )

#     if st.button("Preview Feedback"):
#         conn = get_db_connection()
#         try:
#             with conn.cursor() as cursor:
#                 intervals = {
#                     'last_hour': '1 HOUR',
#                     'last_day': '1 DAY',
#                     'last_week': '1 WEEK',
#                     'last_month': '1 MONTH',
#                     'last_year': '1 YEAR',
#                     'all_time': '100 YEAR'
#                 }
#                 cursor.execute("""
#                     SELECT course_id, assignment, student, file, feedback, suggestions,
#                            need_more_clarity_comment, timestamp 
#                     FROM student_grading_records
#                     WHERE student = %s AND timestamp >= NOW() - INTERVAL %s
#                     ORDER BY timestamp DESC
#                 """, (student_id_input, intervals[time_filter]))
                
#                 data = cursor.fetchall()
#                 if data:
#                     df = pd.DataFrame(data, columns=[
#                         "Course", "Assignment", "student", "File", "Feedback", 
#                         "Suggestions", "Clarification Request", "Timestamp"
#                     ])
#                     st.dataframe(df.style.set_properties(**{
#                         'text-align': 'left',
#                         'white-space': 'pre-wrap'
#                     }))
#                 else:
#                     st.warning("No saved feedback found")
#         except Exception as e:
#             st.error(f"Database error: {str(e)}")
#         finally:
#             conn.close()

#     if st.button("Export to Excel"):
#         conn = get_db_connection()
#         try:
#             with conn.cursor() as cursor:
#                 cursor.execute("""
#                     SELECT * FROM student_grading_records
#                     WHERE student = %s
#                     ORDER BY timestamp DESC
#                 """, (student_id_input,))
                
#                 data = cursor.fetchall()
#                 if data:
#                     df = pd.DataFrame(data, columns=[
#                         "id", "course_id", "assignment", "student", "file",
#                          "feedback", "suggestions",
#                         "need_more_clarity_comment", "timestamp"
#                     ])
                    
#                     output = io.BytesIO()
#                     with pd.ExcelWriter(output, engine='openpyxl') as writer:
#                         df.to_excel(writer, index=False)
                    
#                     st.download_button(
#                         label="📥 Download Excel",
#                         data=output.getvalue(),
#                         file_name=f"student_feedback_{time_filter}.xlsx",
#                         mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
#                     )
#                 else:
#                     st.warning("No data to export")
#         except Exception as e:
#             st.error(f"Database error: {str(e)}")
#         finally:
#             conn.close()

# if __name__ == "__main__":
#     student_dashboard()






