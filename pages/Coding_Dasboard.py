import streamlit as st

st.markdown("# 🚧 Page Under Construction 🚧")
st.markdown("### This feature is coming soon. Stay tuned!")


# import streamlit as st
# import google.generativeai as genai
# import psycopg2
# from psycopg2 import pool
# import os
# import re
# import json
# import uuid
# from dotenv import load_dotenv
# from azure.storage.blob import BlobServiceClient
# from azure.core.exceptions import AzureError

# # Load environment variables
# load_dotenv()

# # Configure Gemini Pro
# try:
#     genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
#     model = genai.GenerativeModel('gemini-1.5-pro-latest')
# except Exception as e:
#     st.error(f"AI configuration failed: {str(e)}")
#     st.stop()

# # Database connection pool initialization
# try:
#     db_pool = psycopg2.pool.ThreadedConnectionPool(
#         minconn=1,
#         maxconn=10,
#         user=os.getenv("POSTGRESQL_USER"),
#         password=os.getenv("POSTGRESQL_PASSWORD"),
#         host=os.getenv("POSTGRESQL_HOST"),
#         port=os.getenv("POSTGRESQL_PORT"),
#         database=os.getenv("POSTGRESQL_NAME")
#     )
# except psycopg2.OperationalError as e:
#     st.error(f"Database connection failed: {str(e)}")
#     st.stop()

# # Azure Blob Storage initialization
# try:
#     blob_service_client = BlobServiceClient.from_connection_string(
#         os.getenv("AZURE_STORAGE_CONNECTION_STRING")
#     )
#     # container_client = blob_service_client.get_container_client("codep-submissions")
#     container_client = blob_service_client.get_container_client("qwasargrade")
# except AzureError as e:
#     st.error(f"Azure Storage connection failed: {str(e)}")
#     st.stop()

# # Session state initialization
# if 'user_id' not in st.session_state:
#     st.session_state.user_id = None
# if 'learning_path' not in st.session_state:
#     st.session_state.learning_path = None
# if 'linux_stage' not in st.session_state:
#     st.session_state.linux_stage = 0
# if 'linux_data' not in st.session_state:
#     st.session_state.linux_data = {}
# if 'programming_stage' not in st.session_state:
#     st.session_state.programming_stage = 0
# if 'programming_data' not in st.session_state:
#     st.session_state.programming_data = {}

# # Database Helper Functions
# def get_db_conn():
#     return db_pool.getconn()

# def release_db_conn(conn):
#     if conn:
#         db_pool.putconn(conn)

# def get_or_create_user(email):
#     conn = None
#     try:
#         conn = get_db_conn()
#         with conn.cursor() as cur:
#             cur.execute("SELECT user_id FROM code_p_users WHERE email = %s", (email,))
#             if cur.rowcount == 0:
#                 cur.execute(
#                     "INSERT INTO code_p_users (email) VALUES (%s) RETURNING user_id",
#                     (email,)
#                 )
#                 user_id = cur.fetchone()[0]
#                 conn.commit()
#             else:
#                 user_id = cur.fetchone()[0]
#             return user_id
#     except Exception as e:
#         if conn:
#             conn.rollback()
#         raise e
#     finally:
#         release_db_conn(conn)


        
        
        
# def save_progress(user_id, path_type, stage, data):
#     conn = None
#     try:
#         conn = get_db_conn()
#         with conn.cursor() as cur:
#             # Add Qwasar support
#             if path_type == "qwasar":
#                 cur.execute("""
#                     INSERT INTO code_p_qwasar_progress 
#                     (user_id, current_stage, qwasar_data)
#                     VALUES (%s, %s, %s)
#                     ON CONFLICT (user_id) DO UPDATE SET
#                         current_stage = EXCLUDED.current_stage,
#                         qwasar_data = EXCLUDED.qwasar_data,
#                         last_updated = NOW()
#                 """, (user_id, stage, json.dumps(data)))
#             else:
#                 # Existing Linux/Programming logic
#                 table = "code_p_linux_progress" if path_type == "linux" else "code_p_programming_progress"
#                 field = "linux_data" if path_type == "linux" else "programming_data"
                
#                 cur.execute(f"""
#                     INSERT INTO {table} (user_id, current_stage, {field})
#                     VALUES (%s, %s, %s)
#                     ON CONFLICT (user_id) DO UPDATE SET
#                         current_stage = EXCLUDED.current_stage,
#                         {field} = EXCLUDED.{field},
#                         last_updated = NOW()
#                 """, (user_id, stage, json.dumps(data)))
#             conn.commit()
#     except Exception as e:
#         if conn:
#             conn.rollback()
#         raise e
#     finally:
#         release_db_conn(conn)        
        
        





# def load_progress(user_id, path_type):
#     conn = None
#     try:
#         conn = get_db_conn()
#         with conn.cursor() as cur:
#             if path_type == "qwasar":
#                 cur.execute("""
#                     SELECT current_stage, qwasar_data FROM code_p_qwasar_progress
#                     WHERE user_id = %s
#                 """, (user_id,))
#             else:
#                 table = "code_p_linux_progress" if path_type == "linux" else "code_p_programming_progress"
#                 field = "linux_data" if path_type == "linux" else "programming_data"
#                 cur.execute(f"""
#                     SELECT current_stage, {field} FROM {table}
#                     WHERE user_id = %s
#                 """, (user_id,))
            
#             result = cur.fetchone()
#             if result:
#                 return (result[0], result[1] or {})
#             return (0, {})
#     except Exception as e:
#         raise e
#     finally:
#         release_db_conn(conn)


        
        
        
# def save_submission(user_id, submission_type, data, status='pending'):
#     conn = None
#     try:
#         # 1. Azure Blob Storage Upload
#         blob_name = f"{user_id}/{submission_type}/{uuid.uuid4()}.json"
#         try:
#             blob_client = container_client.get_blob_client(blob_name)
#             blob_client.upload_blob(json.dumps(data), overwrite=True)
#             st.toast(f"📦 Azure upload successful: {blob_name}")
#         except Exception as azure_error:
#             st.error(f"🚨 Azure upload failed: {str(azure_error)}")
#             return False

#         # 2. Database Insertion
#         conn = get_db_conn()
#         with conn.cursor() as cur:
#             cur.execute("""
#                 INSERT INTO code_p_submissions 
#                 (user_id, submission_type, submission_data, evaluation_results, status)
#                 VALUES (%s, %s, %s, %s, %s)
#             """, (
#                 user_id,
#                 submission_type,
#                 json.dumps({"blob_path": blob_name}),
#                 json.dumps(data.get("results", {})),
#                 status
#             ))
#             conn.commit()
#             st.toast("💾 Database save successful")
#             return True

#     except Exception as e:
#         st.error(f"🔧 Technical Details: {str(e)}")
#         if conn:
#             conn.rollback()
#         return False
#     finally:
#         if conn:
#             release_db_conn(conn)
            
            

# # Data Validation
# def validate_linux_data(data):
#     return {
#         "topic": data.get("topic", "Unspecified"),
#         "difficulty": data.get("difficulty", "Beginner"),
#         "task": data.get("task", ""),
#         "criteria": data.get("criteria", ""),
#         "solution": data.get("solution", ""),
#         "results": data.get("results", {})
#     }

# def validate_programming_data(data):
#     return {
#         "language": data.get("language", "Python"),
#         "difficulty": data.get("difficulty", "Beginner"),
#         "topic": data.get("topic", "General"),
#         "project": data.get("project", ""),
#         "organized_project": data.get("organized_project", ""),
#         "solution": data.get("solution", ""),
#         "results": data.get("results", {})
#     }

# # UI Components
# def email_entry():
#     st.title("CodeP Learning Platform")
#     email = st.text_input("📧 Enter your email to continue:")
    
#     if st.button("Continue"):
#         if re.match(r"^[\w\.-]+@[\w\.-]+\.\w+$", email):
#             try:
#                 st.session_state.user_id = get_or_create_user(email)
#                 st.rerun()
#             except Exception as e:
#                 st.error(f"Database error: {str(e)}")
#         else:
#             st.error("Please enter a valid email address")

#     if st.button("🔍 Run System Check"):
#         st.subheader("System Diagnostics")
        
#         # Check PostgreSQL Connection
#         try:
#             test_conn = get_db_conn()
#             st.success("✅ PostgreSQL: Connection successful")
#             release_db_conn(test_conn)
#         except Exception as e:
#             st.error(f"❌ PostgreSQL: Connection failed - {str(e)}")
        
#         # Check Azure Connection
#         try:
#             container_client.get_container_properties()
#             st.success("✅ Azure Blob: Connection successful")
#         except Exception as e:
#             st.error(f"❌ Azure Blob: Connection failed - {str(e)}")
        
#         # Check Table Existence
#         try:
#             conn = get_db_conn()
#             with conn.cursor() as cur:
#                 cur.execute("""
#                     SELECT EXISTS (
#                         SELECT FROM information_schema.tables 
#                         WHERE table_name = 'code_p_submissions'
#                     )
#                 """)
#                 exists = cur.fetchone()[0]
#                 st.success(f"✅ Table Check: code_p_submissions exists? {'Yes' if exists else 'No'}")
#             release_db_conn(conn)
#         except Exception as e:
#             st.error(f"❌ Table Check Failed: {str(e)}")




# def linux_path():
#     st.header("🐧 Linux System Skills Evaluation")
    
#     if st.session_state.linux_stage == 0:
#         with st.form("linux_config"):
#             col1, col2 = st.columns(2)
#             with col1:
#                 topic = st.selectbox(
#                     "Select Linux Domain:",
#                     ["Filesystem Management", "Process Control", "Security Hardening",
#                      "Networking", "Package Management", "Shell Scripting"],
#                     index=None
#                 )
#             with col2:
#                 difficulty = st.selectbox(
#                     "Select Difficulty Level:",
#                     ["Beginner", "Intermediate", "Advanced", "Expert"],
#                     index=None
#                 )
            
#             if st.form_submit_button("Begin Evaluation"):
#                 if topic and difficulty:
#                     st.session_state.linux_data = validate_linux_data({
#                         "topic": topic,
#                         "difficulty": difficulty
#                     })
#                     st.session_state.linux_stage = 1
#                     st.rerun()
#                 else:
#                     st.warning("Please select both domain and difficulty level")

#     elif st.session_state.linux_stage == 1:
#         st.subheader("Generate Evaluation Task")
        
#         if not st.session_state.linux_data.get("task"):
#             with st.spinner("Creating Linux challenge..."):
#                 try:
#                     prompt = f"""Create a {st.session_state.linux_data['difficulty']} level Linux task focused on {
#                         st.session_state.linux_data['topic']}. Include:
#                     - Clear objectives
#                     - Required commands/scripts
#                     - Validation steps
#                     - Common pitfalls
#                     - Enterprise relevance"""
#                     response = model.generate_content(prompt)
#                     st.session_state.linux_data["task"] = response.text
#                 except Exception as e:
#                     st.error(f"Task generation failed: {str(e)}")
        
#         if st.session_state.linux_data.get("task") and not st.session_state.linux_data.get("criteria"):
#             with st.spinner("Creating evaluation criteria..."):
#                 try:
#                     prompt = f"""Create evaluation criteria for:
#                     {st.session_state.linux_data["task"]}
#                     Focus on:
#                     - Command efficiency
#                     - Security best practices
#                     - Documentation quality
#                     - Error handling
#                     - Enterprise standards"""
#                     response = model.generate_content(prompt)
#                     st.session_state.linux_data["criteria"] = response.text
#                 except Exception as e:
#                     st.error(f"Criteria generation failed: {str(e)}")

#         if st.session_state.linux_data.get("task"):
#             with st.expander("View Task Details", expanded=True):
#                 st.write(st.session_state.linux_data["task"])
            
#             with st.expander("Evaluation Criteria"):
#                 st.write(st.session_state.linux_data["criteria"])
            
#             if st.button("Proceed to Solution Submission"):
#                 st.session_state.linux_stage = 2
#                 st.rerun()

#     elif st.session_state.linux_stage == 2:
#         st.subheader("Submit Your Solution")
        
#         tab1, tab2 = st.tabs(["📁 Upload Files", "📝 Paste Solution"])
#         solution_content = ""
        
#         with tab1:
#             uploaded_files = st.file_uploader(
#                 "Upload Solution Files:",
#                 type=['.sh', '.conf', '.service', '.md'],
#                 accept_multiple_files=True
#             )
#             if uploaded_files:
#                 solution_content += "\n\n".join(
#                     [f"### {f.name}\n{f.getvalue().decode('utf-8')}" for f in uploaded_files]
#                 )
        
#         with tab2:
#             pasted_solution = st.text_area("Paste Your Solution:", height=300)
#             if pasted_solution.strip():
#                 solution_content += f"\n\n### Pasted Solution\n{pasted_solution}"
        
#         if st.button("Evaluate Solution"):
#             if not solution_content.strip():
#                 st.warning("Please upload files or paste your solution")
#             else:
#                 with st.spinner("Analyzing solution..."):
#                     try:
#                         prompt = f"""Linux Task:
#                         {st.session_state.linux_data['task']}
                        
#                         Evaluation Criteria:
#                         {st.session_state.linux_data['criteria']}
                        
#                         Submitted Solution:
#                         {solution_content}
                        
#                         Provide analysis covering:
#                         1. Solution correctness
#                         2. Security best practices
#                         3. Alternative approaches
#                         4. Improvement suggestions
#                         5. Production readiness
                        
#                         Format response as:
#                         Correctness: [Correct/Partial/Incorrect]
#                         Security: [Security assessment]
#                         Alternatives: [Alternative solutions]
#                         Suggestions: [Improvement steps]
#                         Readiness: [Production viability]"""
                        
#                         response = model.generate_content(prompt)
#                         response_text = response.text

#                         results = {
#                             "correctness": re.search(r"Correctness:\s*(.*)", response_text).group(1) if re.search(r"Correctness:", response_text) else "N/A",
#                             "security": re.search(r"Security:\s*(.*?)(?=\nAlternatives:)", response_text, re.DOTALL).group(1).strip() if re.search(r"Security:", response_text) else "",
#                             "alternatives": re.search(r"Alternatives:\s*(.*?)(?=\nSuggestions:)", response_text, re.DOTALL).group(1).strip() if re.search(r"Alternatives:", response_text) else "",
#                             "suggestions": re.search(r"Suggestions:\s*(.*?)(?=\nReadiness:)", response_text, re.DOTALL).group(1).strip() if re.search(r"Suggestions:", response_text) else "",
#                             "readiness": re.search(r"Readiness:\s*(.*)", response_text).group(1) if re.search(r"Readiness:", response_text) else ""
#                         }
                        
#                         st.session_state.linux_data["results"] = results
#                         st.session_state.linux_stage = 3
#                         st.rerun()

#                     except Exception as e:
#                         st.error(f"Evaluation failed: {str(e)}")

#     elif st.session_state.linux_stage == 3:
#         st.subheader("Evaluation Results")
#         results = st.session_state.linux_data.get("results", {})
        
#         col1, col2 = st.columns(2)
#         with col1:
#             st.metric("Solution Correctness", results.get("correctness", "N/A"))
#             st.metric("Production Readiness", results.get("readiness", "N/A"))
#         with col2:
#             st.write("**Security Assessment**")
#             st.info(results.get("security", "No security assessment available"))
        
#         with st.expander("Alternative Approaches", expanded=True):
#             st.write(results.get("alternatives", "No alternatives suggested"))
        
#         with st.expander("Improvement Suggestions"):
#             st.write(results.get("suggestions", "No suggestions available"))
        
#         col1, col2 = st.columns(2)
#         with col1:
#             if st.button("🔄 Try Again"):
#                 st.session_state.linux_stage = 2
#                 st.rerun()
            
#             if st.button("🆕 New Linux Task"):
#                 st.session_state.linux_data = validate_linux_data({
#                     "topic": st.session_state.linux_data.get("topic"),
#                     "difficulty": st.session_state.linux_data.get("difficulty")
#                 })
#                 st.session_state.linux_stage = 1
#                 st.rerun()

#         with col2:
#             if st.button("✅ Approve & Save", type="primary"):
#                 success = save_submission(
#                     st.session_state.user_id,
#                     "linux",
#                     {
#                         "task": st.session_state.linux_data.get("task", ""),
#                         "solution": st.session_state.linux_data.get("solution", ""),
#                         "results": results
#                     },
#                     status="approved"
#                 )
#                 if success:
#                     st.success("Solution approved and saved!")
#                 else:
#                     st.error("Failed to save submission. Please try again.")
            
#             if st.button("💻 Switch to Programming"):
#                 st.session_state.learning_path = "Programming"
#                 st.rerun()

#         st.markdown("---")
#         if st.button("🏠 Return to Main Menu"):
#             st.session_state.learning_path = None
#             st.rerun()

# def programming_path():
#     st.header("💻 Programming Projects Path")
    
#     if st.session_state.programming_stage == 0:
#         with st.form("prog_config"):
#             col1, col2, col3 = st.columns(3)
#             with col1:
#                 language = st.selectbox(
#                     "Select Language:",
#                     ["Python", "JavaScript", "Java", "C++", "Go", "Rust"],
#                     index=None
#                 )
#             with col2:
#                 difficulty = st.selectbox(
#                     "Difficulty Level:",
#                     ["Beginner", "Intermediate", "Advanced", "Expert"],
#                     index=None
#                 ) if language else None
#             with col3:
#                 topic = st.selectbox(
#                     "Project Topic:",
#                     ["Web Development", "Data Analysis", "Systems Programming"] if language else [],
#                     index=None
#                 ) if language and difficulty else None
            
#             if st.form_submit_button("Generate Project"):
#                 if language and difficulty and topic:
#                     st.session_state.programming_data = validate_programming_data({
#                         "language": language,
#                         "difficulty": difficulty,
#                         "topic": topic
#                     })
#                     st.session_state.programming_stage = 1
#                     st.rerun()
#                 else:
#                     st.warning("Please complete all selections")

#     elif st.session_state.programming_stage == 1:
#         st.subheader("Project Setup")
        
#         if not st.session_state.programming_data.get("project"):
#             with st.spinner("Creating programming project..."):
#                 try:
#                     prompt = f"""Create a {st.session_state.programming_data['difficulty']} level {
#                         st.session_state.programming_data['language']} project focused on {
#                         st.session_state.programming_data['topic']}. Include:
#                     - Detailed requirements
#                     - Technical specifications
#                     - Success criteria
#                     - Suggested implementation
#                     - Testing guidelines"""
#                     response = model.generate_content(prompt)
#                     st.session_state.programming_data["project"] = response.text
#                 except Exception as e:
#                     st.error(f"Project generation failed: {str(e)}")
        
#         if st.session_state.programming_data.get("project"):
#             if st.button("✨ Organize Question Format"):
#                 with st.spinner("Formatting project description..."):
#                     try:
#                         prompt = f"""Organize this project description into structured markdown:
#                         {st.session_state.programming_data["project"]}
#                         Include sections: Objectives, Requirements, Implementation, Testing"""
#                         response = model.generate_content(prompt)
#                         st.session_state.programming_data["organized_project"] = response.text
#                     except Exception as e:
#                         st.error(f"Formatting failed: {str(e)}")
            
#             display_text = st.session_state.programming_data.get(
#                 "organized_project", 
#                 st.session_state.programming_data["project"]
#             )
#             st.markdown(f"```markdown\n{display_text}\n```")
            
#             tab1, tab2 = st.tabs(["📁 Upload Code", "📝 Paste Code"])
#             solution_content = ""
            
#             with tab1:
#                 uploaded_files = st.file_uploader(
#                     "Upload Solution Files:",
#                     type=['.py', '.js', '.java', '.cpp', '.go', '.rs'],
#                     accept_multiple_files=True
#                 )
#                 if uploaded_files:
#                     solution_content += "\n\n".join(
#                         [f"### {f.name}\n{f.getvalue().decode('utf-8')}" for f in uploaded_files]
#                     )
            
#             with tab2:
#                 pasted_code = st.text_area("Paste Your Code:", height=300)
#                 if pasted_code.strip():
#                     solution_content += f"\n\n### Pasted Code\n{pasted_code}"
            
#             if st.button("Evaluate Solution"):
#                 if not solution_content.strip():
#                     st.warning("Please upload files or paste your code")
#                 else:
#                     with st.spinner("Analyzing code..."):
#                         try:
#                             prompt = f"""Project Requirements:
#                             {st.session_state.programming_data["project"]}
                            
#                             Submitted Solution:
#                             {solution_content}
                            
#                             Evaluate based on:
#                             - Code quality
#                             - Requirements fulfillment
#                             - Best practices
#                             - Error handling
#                             - Efficiency
                            
#                             Format response as:
#                             Grade: [A/B/C/D/F]
#                             Analysis: [Technical analysis]
#                             Improvements: [Suggested improvements]"""
                            
#                             response = model.generate_content(prompt)
#                             response_text = response.text

#                             results = {
#                                 "grade": re.search(r"Grade:\s*(.*)", response_text).group(1) if re.search(r"Grade:", response_text) else "N/A",
#                                 "analysis": re.search(r"Analysis:\s*(.*?)(?=\nImprovements:)", response_text, re.DOTALL).group(1).strip() if re.search(r"Analysis:", response_text) else "",
#                                 "improvements": re.search(r"Improvements:\s*(.*)", response_text, re.DOTALL).group(1).strip() if re.search(r"Improvements:", response_text) else ""
#                             }
                            
#                             st.session_state.programming_data["results"] = results
#                             st.session_state.programming_stage = 2
#                             st.rerun()

#                         except Exception as e:
#                             st.error(f"Evaluation failed: {str(e)}")

#     elif st.session_state.programming_stage == 2:
#         st.subheader("Evaluation Results")
#         results = st.session_state.programming_data.get("results", {})
        
#         col1, col2 = st.columns([1, 3])
#         with col1:
#             st.metric("Project Grade", results.get("grade", "N/A"))
#         with col2:
#             st.write("**Technical Analysis**")
#             st.info(results.get("analysis", "No analysis available"))
        
#         with st.expander("Improvement Suggestions", expanded=True):
#             st.write(results.get("improvements", "No suggestions available"))
        
#         col1, col2 = st.columns(2)
#         with col1:
#             if st.button("🔄 Try Again"):
#                 st.session_state.programming_stage = 1
#                 st.rerun()
            
#             if st.button("🆕 New Project"):
#                 st.session_state.programming_data = validate_programming_data({
#                     "language": st.session_state.programming_data.get("language"),
#                     "difficulty": st.session_state.programming_data.get("difficulty"),
#                     "topic": st.session_state.programming_data.get("topic")
#                 })
#                 st.session_state.programming_stage = 1
#                 st.rerun()

#         with col2:
#             if st.button("✅ Approve & Save", type="primary"):
#                 try:
#                     save_submission(
#                         st.session_state.user_id,
#                         "programming",
#                         {
#                             "project": st.session_state.programming_data.get("project", ""),
#                             "solution": st.session_state.programming_data.get("solution", ""),
#                             "results": results
#                         },
#                         status="approved"
#                     )
#                     st.success("Solution approved and saved!")
#                 except Exception as e:
#                     st.error(f"Save failed: {str(e)}")
            
#             if st.button("🐧 Switch to Linux"):
#                 st.session_state.learning_path = "Linux"
#                 st.rerun()

#         st.markdown("---")
#         if st.button("🏠 Return to Main Menu"):
#             st.session_state.learning_path = None
#             st.rerun()











# # Add to LEARNING_PATHS configuration
# LEARNING_PATHS = [
#     "Linux System Skills",
#     "Programming Projects",
#     "Qwasar Questions"
# ]

# # Add Qwasar content database (you can move this to actual DB later)
# QWASAR_CONTENT = {
#     "Preseason": """[Preseason Content]
#     Basic programming concepts
#     Introduction to algorithms
#     Data types and structures
#     Control flow and functions""",
    
#     "Season 01": """[Season 01]
#     Advanced data structures
#     Algorithm complexity
#     Recursion and iteration
#     Basic system programming""",
    
#     "Season 02": """[Season 02]
#     Memory management
#     File I/O operations
#     Network programming
#     Concurrent programming""",
    
#     "Season 03": """[Season 03]
#     Distributed systems
#     Cloud computing concepts
#     Advanced security topics
#     Performance optimization""",
    
#     "Preseason web": """[Preseason web]
# Preseason Web
# Dive into practical coding exercises both front-end and back-end development, mastering fundamental programming concepts, languages like Ruby, JavaScript, HTML, and CSS, as well as database management, object-oriented design, and cloud deployment, preparing for real-world job interviews with extensive role plays and resume reviews.

# Js Quest01
# Learn simnple codes in foundational programming concepts through CSS, HTML, and JavaScript, focusing on integer variables and console log printing.
# Js Quest02
# Understand and utilize different variable types effectively and practice code questions.
# Js Quest03
# Generte code questions that shows how to Develop reusable code with loops, functions, and function parameters.
# Js Quest04
# Generte code questions that shows how to Automate tasks using scripts and terminal commands, integrating functions and conditional statements.

# provide code questions Projects for each of this (13)
# Js Quest01
# Js Quest02
# Js Quest03
# Js Quest04
# Js Quest05
# Js Quest06
# Js Quest07
# My Levenshtein
# My Moving Box Realtime
# My Spaceship
# My Css Is Easy I
# My Bouncing Box
# My First Backend
# Exercises 11
# Hello Name
# My Add
# My Array Uniq
# My Count On It
# My Each
# My Fibonacci
# My Putstr
# My Recursive Pow
# My Strchr
# My String Formatting
# My String Index
# """

# }

# # Add to session state initialization
# if 'qwasar_stage' not in st.session_state:
#     st.session_state.qwasar_stage = 0
# if 'qwasar_data' not in st.session_state:
#     st.session_state.qwasar_data = {}

# def retrieve_qwasar_content(season):
#     return QWASAR_CONTENT.get(season, "No content available for this season")


# from datetime import datetime



# def qwasar_path():
#     st.header("🏫 Qwasar Training Program")
    
#     # Initialize session state with safe defaults
#     if 'qwasar_data' not in st.session_state:
#         st.session_state.qwasar_data = {
#             "season": "",
#             "content": "",
#             "questions": [],
#             "current_question_index": 0,
#             "solutions": [],
#             "results": [],
#             "generated_raw_content": ""
#         }

#     qd = st.session_state.qwasar_data

#     # Validate and synchronize data
#     try:
#         # Ensure solutions array matches questions
#         if len(qd["solutions"]) != len(qd["questions"]):
#             qd["solutions"] = [{"solution": "", "results": {}} for _ in qd["questions"]]
        
#         # Clamp current index to valid range
#         qd["current_question_index"] = max(0, min(
#             qd["current_question_index"], 
#             len(qd["questions"]) - 1
#         ))

#     except Exception as e:
#         st.error(f"Data validation error: {str(e)}")
#         st.session_state.qwasar_data = {
#             "season": "",
#             "content": "",
#             "questions": [],
#             "current_question_index": 0,
#             "solutions": [],
#             "results": [],
#             "generated_raw_content": ""
#         }
#         st.rerun()

#     if st.session_state.qwasar_stage == 0:
#         # Stage 0: Season Selection
#         st.subheader("Select Qwasar Season")
#         selected_season = st.selectbox(
#             "Choose your season:",
#             ["Preseason", "Season 01", "Season 02", "Season 03"],
#             index=0
#         )
        
#         col1, col2 = st.columns([3, 1])
#         with col1:
#             if st.button("Load Season Content"):
#                 qd["season"] = selected_season
#                 qd["content"] = retrieve_qwasar_content(selected_season)
#                 st.session_state.qwasar_stage = 1
#                 st.rerun()
        
#         with col2:
#             if st.button("← Main Menu"):
#                 st.session_state.learning_path = None
#                 st.rerun()

#     elif st.session_state.qwasar_stage == 1:
#         # Stage 1: Content Display and Path Generation
#         st.subheader(f"{qd['season']} Content")
#         st.markdown(f"```\n{qd['content']}\n```")
        
#         col1, col2 = st.columns([2, 1])
#         with col1:
#             if st.button("Generate Learning Path"):
#                 with st.spinner("Creating personalized learning path..."):
#                     try:
#                         # Generate learning path prompt
#                         prompt = f"""Create a progressive learning path for {qd['season']} with STRICT formatting:
# Produce EXACTLY 15 items (5 beginner/5 intermediate/5 advanced) formatted as:

# ### BEGINNER QUESTIONS
# 1. [Concise question text]
# 2. [Concise question text]
# 3. [Concise question text]
# 4. [Concise question text]
# 5. [Concise question text]

# ### INTERMEDIATE EXERCISES
# 1. [Clear exercise description]
# 2. [Clear exercise description]
# 3. [Clear exercise description]
# 4. [Clear exercise description]
# 5. [Clear exercise description]

# ### ADVANCED PROJECTS
# 1. [Project specification]
# 2. [Project specification]
# 3. [Project specification]
# 4. [Project specification]
# 5. [Project specification]

# Base this on: {qd['content']}"""

#                         response = model.generate_content(prompt)
#                         if not response.text:
#                             raise ValueError("Empty response from AI model")
                        
#                         generated_content = response.text
#                         qd["generated_raw_content"] = generated_content

#                         # Parse generated content with improved regex
#                         sections = {
#                             "beginner": {"pattern": r"(?i)### BEGINNER QUESTIONS?.*?\n(.*?)(?=\n### INTERMEDIATE)", "items": []},
#                             "intermediate": {"pattern": r"(?i)### INTERMEDIATE EXERCISES?.*?\n(.*?)(?=\n### ADVANCED)", "items": []},
#                             "advanced": {"pattern": r"(?i)### ADVANCED PROJECTS?.*?\n(.*)", "items": []}
#                         }

#                         for section in sections:
#                             match = re.search(sections[section]["pattern"], generated_content, re.DOTALL)
#                             if match:
#                                 items = [
#                                     re.sub(r"^\d+\.\s*", "", line.strip()).strip('[]')
#                                     for line in match.group(1).split('\n')
#                                     if line.strip() and re.match(r"^\d+\.", line)
#                                 ][:5]
#                                 sections[section]["items"] = items

#                         # Validate parsed content
#                         error_flag = False
#                         for section in sections:
#                             if len(sections[section]["items"]) != 5:
#                                 st.error(f"Invalid {section} items count: {len(sections[section]['items'])}/5")
#                                 error_flag = True

#                         if error_flag:
#                             raise ValueError("Invalid learning path structure")

#                         # Structure questions
#                         qd["questions"] = (
#                             [{"type": "beginner", "text": q} for q in sections["beginner"]["items"]] +
#                             [{"type": "intermediate", "text": q} for q in sections["intermediate"]["items"]] +
#                             [{"type": "advanced", "text": q} for q in sections["advanced"]["items"]]
#                         )

#                         # Initialize solutions
#                         qd["solutions"] = [{"solution": "", "results": {}} for _ in qd["questions"]]
#                         qd["current_question_index"] = 0
                        
#                         st.session_state.qwasar_stage = 2
#                         st.rerun()

#                     except Exception as e:
#                         st.error(f"""
#                             **Path Generation Failed**: {str(e)}
#                             - Please try the generate button again
#                             - Common fixes: Check API key, retry generation
#                             - Raw content for debugging:
#                             ```{generated_content[:500]}...```
#                         """)

#         with col2:
#             if st.button("← Back"):
#                 st.session_state.qwasar_stage = 0
#                 st.rerun()

#     elif st.session_state.qwasar_stage == 2:
#         # Stage 2: Question Progression
#         st.subheader("Learning Path Progression")
        
#         # Handle empty questions case
#         if not qd["questions"]:
#             st.error("No questions available! Generating new set...")
#             st.session_state.qwasar_stage = 1
#             st.rerun()

#         # Navigation controls
#         col1, col2, col3 = st.columns([2, 6, 2])
#         with col1:
#             if st.button("← Previous") and qd["current_question_index"] > 0:
#                 qd["current_question_index"] -= 1
#                 st.rerun()
        
#         with col3:
#             if st.button("Next →") and qd["current_question_index"] < len(qd["questions"]) - 1:
#                 qd["current_question_index"] += 1
#                 st.rerun()

#         # Current question display
#         current_idx = qd["current_question_index"]
#         question = qd["questions"][current_idx]
#         st.markdown(f"""
#             ### Question {current_idx + 1} of {len(qd['questions'])}
#             **Level:** {question['type'].title()}  
#             **Challenge:** {question['text']}
#         """)

#         # Solution input section
#         st.markdown("---")
#         st.subheader("Your Solution")
#         tab1, tab2 = st.tabs(["📁 Upload Solution", "📝 Code Editor"])
        
#         current_solution = qd["solutions"][current_idx]
        
#         with tab1:
#             uploaded_files = st.file_uploader(
#                 "Upload solution files",
#                 type=['py', 'js', 'java', 'c', 'cpp'],
#                 accept_multiple_files=True,
#                 key=f"upload_{current_idx}"
#             )
#             if uploaded_files:
#                 current_solution["solution"] = "\n".join(
#                     [f.read().decode() for f in uploaded_files]
#                 )

#         with tab2:
#             code = st.text_area(
#                 "Write your code here",
#                 value=current_solution["solution"],
#                 height=400,
#                 key=f"editor_{current_idx}"
#             )
#             current_solution["solution"] = code

#         # Evaluation section
#         st.markdown("---")
#         if st.button("Evaluate Solution", key=f"eval_{current_idx}"):
#             if not current_solution["solution"].strip():
#                 st.warning("Please provide a solution before evaluating")
#             else:
#                 with st.spinner("Analyzing solution..."):
#                     try:
#                         prompt = f"""
#                         **ROLE**: You are a Qwasar technical evaluator. Analyze this solution strictly:

#                         **Question:** {question['text']}
#                         **Solution:** {current_solution["solution"]}
                        
                        
#                         **REQUIRED FORMAT** (JSON):
#                         {{
#                             "requirements_score": 0-10,
#                             "quality_score": 0-10,
#                             "efficiency_score": 0-10,
#                             "best_practices": "text",
#                             "improvements": ["list"],
#                             "summary": "text"
#                         }}
                        
                        
#                        **EVALUATION CRITERIA**:
#                        1. Requirements fulfillment (exact match to question)
#                        2. Code quality (readability, structure)
#                        3. Efficiency (optimal implementation)
#                        4. Security best practices
#                        5. Enterprise standards
#                        """
                        
#                         response = model.generate_content(prompt)
#                         # results = json.loads(response.text)
                        
#                         # # Validate scores
#                         # for key in ["requirements_score", "quality_score", "efficiency_score"]:
#                         #     if not 0 <= results.get(key, 0) <= 10:
#                         #         raise ValueError(f"Invalid {key} value")

#                         # current_solution["results"] = {
#                         #     **results,
#                         #     "timestamp": datetime.now().isoformat()
#                         # }
                        
#                         # st.success("Evaluation stored successfully!")
#                         # if current_idx < len(qd["questions"]) - 1:
#                         #     qd["current_question_index"] += 1
#                         #     st.rerun()
                        
                        
#                         # Validate response before parsing
#                         if not response.text.strip():
#                             raise ValueError("Empty response from AI evaluator")
                
#                         # Clean response text
#                         response_text = response.text.replace("```json", "").replace("```", "").strip()
                
#                         try:
#                             results = json.loads(response_text)
#                         except json.JSONDecodeError:
#                             # Attempt to fix malformed JSON
#                             corrected_response = model.generate_content(
#                                 f"Fix this JSON:\n{response_text}\nOutput ONLY valid JSON:"
#                             )
#                             results = json.loads(corrected_response.text)

#                         # Validate scores
#                         score_fields = ["requirements_score", "quality_score", "efficiency_score"]
#                         for field in score_fields:
#                             if not 0 <= results.get(field, -1) <= 10:
#                                 raise ValueError(f"Invalid {field} value: {results.get(field)}")

#                         current_solution["results"] = {
#                             **results,
#                             "timestamp": datetime.now().isoformat(),
#                             "raw_response": response_text  # Store for debugging
#                         }
                
#                         st.success("Evaluation completed successfully!")
#                         if current_idx < len(qd["questions"]) - 1:
#                             qd["current_question_index"] += 1
#                             st.rerun()                        
                        
                        
                        
#                     except Exception as e:
#                         # st.error(f"Evaluation failed: {str(e)}")
#                         st.error(f"""
#                             **Evaluation Failed**: {str(e)}
#                             - Common fixes:
#                               1. Ensure solution addresses all question requirements
#                               2. Check for syntax errors in code
#                               3. Try simplifying complex solutions
#                             - Technical Details: {e}
#                             - AI Response: {getattr(response, 'text', 'N/A')}
#                         """)
#                         # Store error state for debugging
#                         current_solution["error"] = {
#                             "message": str(e),
#                             "response": getattr(response, 'text', ''),
#                             "timestamp": datetime.now().isoformat()
#                         }





#         # Progress tracking
#         st.markdown("---")
#         completed = sum(1 for s in qd["solutions"] if s["solution"].strip())
#         st.progress(completed / len(qd["solutions"]))
        
#         if st.button("Complete Season", disabled=completed < len(qd["solutions"])):
#             st.session_state.qwasar_stage = 3
#             st.rerun()

#         # Navigation footer
#         st.markdown("---")
#         col1, col2 = st.columns([1, 1])
#         with col1:
#             if st.button("← Back to Content"):
#                 st.session_state.qwasar_stage = 1
#                 st.rerun()
#         with col2:
#             if st.button("🏠 Main Menu"):
#                 st.session_state.learning_path = None
#                 st.rerun()

#     elif st.session_state.qwasar_stage == 3:
#         # Stage 3: Completion Summary
#         st.subheader("Season Completion Summary")
#         st.balloons()
#         st.success(f"Congratulations on completing {qd['season']}!")
        
#         # Results summary
#         st.markdown("### Final Scores")
#         scores = {
#             "Beginner": [],
#             "Intermediate": [],
#             "Advanced": []
#         }
        
#         for idx, (question, solution) in enumerate(zip(qd["questions"], qd["solutions"])):
#             scores[question["type"].title()].append(
#                 solution.get("results", {}).get("requirements_score", 0)
#             )
        
#         col1, col2, col3 = st.columns(3)
#         with col1:
#             st.metric("Beginner Avg", f"{np.mean(scores['Beginner']):.1f}/10")
#         with col2:
#             st.metric("Intermediate Avg", f"{np.mean(scores['Intermediate']):.1f}/10")
#         with col3:
#             st.metric("Advanced Avg", f"{np.mean(scores['Advanced']):.1f}/10")

#         # Detailed results
#         with st.expander("View Detailed Results"):
#             for idx, (question, solution) in enumerate(zip(qd["questions"], qd["solutions"])):
#                 st.markdown(f"""
#                     ### Question {idx + 1} ({question['type'].title()})
#                     **Challenge:** {question['text']}
#                     **Last Evaluated:** {solution.get("results", {}).get("timestamp", "N/A")}
#                     **Requirements Score:** {solution.get("results", {}).get("requirements_score", "N/A")}/10
#                     **Quality Score:** {solution.get("results", {}).get("quality_score", "N/A")}/10
#                     **Efficiency Score:** {solution.get("results", {}).get("efficiency_score", "N/A")}/10
#                 """)
#                 if solution.get("results"):
#                     st.markdown("#### Best Practices Feedback")
#                     st.info(solution["results"].get("best_practices", "No feedback available"))
                    
#                     st.markdown("#### Improvement Suggestions")
#                     st.write("\n".join([f"- {s}" for s in solution["results"].get("improvements", [])]))
                
#                 st.markdown("---")

#         # Final actions
#         st.markdown("### Next Steps")
#         col1, col2, col3 = st.columns(3)
#         with col1:
#             if st.button("📥 Download Report"):
#                 report = json.dumps(qd, indent=2)
#                 st.download_button(
#                     label="Download JSON Report",
#                     data=report,
#                     file_name=f"qwasar_{qd['season']}_report.json",
#                     mime="application/json"
#                 )
#         with col2:
#             if st.button("🔄 New Season"):
#                 st.session_state.qwasar_stage = 0
#                 st.session_state.qwasar_data = {
#                     "season": "",
#                     "content": "",
#                     "questions": [],
#                     "current_question_index": 0,
#                     "solutions": [],
#                     "results": [],
#                     "generated_raw_content": ""
#                 }
#                 st.rerun()
#         with col3:
#             if st.button("🏠 Main Menu"):
#                 st.session_state.learning_path = None
#                 st.rerun()

#     # Debug panel
#     if os.getenv("DEBUG_MODE"):
#         with st.expander("Debug Information"):
#             st.write("Current Stage:", st.session_state.qwasar_stage)
#             st.write("Questions:", len(qd["questions"]))
#             st.write("Solutions:", len(qd["solutions"]))
#             st.write("Current Index:", qd["current_question_index"])
#             st.write("Raw Content Preview:", qd.get("generated_raw_content", "")[:300] + "...")





# # def validate_qwasar_data(data):
# #     return {
# #         "season": data.get("season", "Preseason"),
# #         "content": data.get("content", ""),
# #         "generated_questions": data.get("generated_questions", ""),
# #         "solution": data.get("solution", ""),
# #         "results": data.get("results", {})
# #     }
    
# def validate_qwasar_data(data):
#     validated = {
#         "season": data.get("season", "Preseason"),
#         "content": data.get("content", ""),
#         "questions": data.get("questions", []),
#         "current_question_index": data.get("current_question_index", 0),
#         "solutions": data.get("solutions", [{} for _ in range(15)]),  # 15 empty solutions
#         "results": data.get("results", []),
#         "generated_questions": data.get("generated_questions", "")
#     }
    
#     # Ensure solutions array matches question count
#     if len(validated["questions"]) > 0:
#         validated["solutions"] = validated["solutions"][:len(validated["questions"])]
#         validated["solutions"] += [{}] * (len(validated["questions"]) - len(validated["solutions"]))
    
#     return validated








# ## ADMIN PANEL
# # Add this section before the main() function
# def admin_panel():
#     st.title("🔧 Admin Dashboard")
    
#     # System health check function
#     def check_system_health():
#         status = {
#             "database": False,
#             "storage": False,
#             "ai": False
#         }
        
#         try:
#             test_conn = get_db_conn()
#             status["database"] = True
#             release_db_conn(test_conn)
#         except:
#             pass
        
#         try:
#             container_client.get_container_properties()
#             status["storage"] = True
#         except:
#             pass
        
#         try:
#             model.generate_content("Test connection")
#             status["ai"] = True
#         except:
#             pass
        
#         return status

#     tab1, tab2, tab3 = st.tabs(["System Health", "User Management", "Content Management"])
    
#     with tab1:
#         st.subheader("System Status")
#         health = check_system_health()
        
#         col1, col2, col3 = st.columns(3)
#         col1.metric("Database", "✅ Online" if health["database"] else "❌ Offline")
#         col2.metric("Storage", "✅ Online" if health["storage"] else "❌ Offline")
#         col3.metric("AI Service", "✅ Online" if health["ai"] else "❌ Offline")
        
#         if st.button("Run Full Diagnostic"):
#             with st.expander("Detailed Diagnostics"):
#                 st.code(f"""
#                     Database Connection: {health['database']}
#                     Storage Connection: {health['storage']}
#                     AI Connection: {health['ai']}
                    
#                     Environment Variables:
#                     - PostgreSQL: {'✅' if os.getenv("POSTGRESQL_HOST") else '❌'}
#                     - Azure Storage: {'✅' if os.getenv("AZURE_STORAGE_CONNECTION_STRING") else '❌'}
#                     - Gemini API: {'✅' if os.getenv("GOOGLE_API_KEY") else '❌'}
#                 """)
    
#     with tab2:
#         st.subheader("User Management")
#         if st.button("Refresh User List"):
#             try:
#                 conn = get_db_conn()
#                 with conn.cursor() as cur:
#                     cur.execute("""
#                         SELECT u.user_id, u.email, 
#                                COUNT(s.submission_id) AS submissions,
#                                MAX(s.submitted_at) AS last_activity
#                         FROM code_p_users u
#                         LEFT JOIN code_p_submissions s ON u.user_id = s.user_id
#                         GROUP BY u.user_id
#                         ORDER BY last_activity DESC
#                     """)
#                     results = cur.fetchall()
                    
#                     st.dataframe(
#                         data=results,
#                         columns=["ID", "Email", "Submissions", "Last Activity"],
#                         use_container_width=True
#                     )
#             except Exception as e:
#                 st.error(f"Failed to load users: {str(e)}")
#             finally:
#                 release_db_conn(conn)
    
#     with tab3:
#         st.subheader("Content Management")
#         st.write("Qwasar Curriculum Version Control")
        
#         selected_season = st.selectbox(
#             "Select Season to Update",
#             ["Preseason", "Season 01", "Season 02", "Season 03"]
#         )
        
#         new_content = st.text_area(
#             f"Update {selected_season} Content",
#             value=QWASAR_CONTENT.get(selected_season, ""),
#             height=300
#         )
        
#         if st.button("Update Content"):
#             QWASAR_CONTENT[selected_season] = new_content
#             st.success(f"{selected_season} content updated successfully")

#     if st.button("Exit Admin Mode"):
#         st.session_state.clear()
#         st.rerun()






# # Main Application Flow
# def main():
#     if not st.session_state.user_id:
#         email_entry()
#     else:
#         if not st.session_state.learning_path:
#             st.title("Choose Your Learning Path")
            
#             # Path selection columns
#             cols = st.columns(3)
#             with cols[0]:
#                 if st.button("🐧 Linux System Skills"):
#                     st.session_state.learning_path = "Linux"
#                     st.rerun()
#             with cols[1]:
#                 if st.button("💻 Programming Projects"):
#                     st.session_state.learning_path = "Programming"
#                     st.rerun()
#             with cols[2]:
#                 if st.button("🏫 Qwasar Questions"):
#                     st.session_state.learning_path = "Qwasar"
#                     st.rerun()

#             # Progress display
#             st.markdown("---")
#             st.subheader("Learning Progress")
#             try:
#                 conn = get_db_conn()
#                 with conn.cursor() as cur:
#                     # Completed challenges
#                     cur.execute("""
#                         SELECT submission_type, COUNT(*) 
#                         FROM code_p_submissions 
#                         WHERE user_id = %s AND status = 'approved'
#                         GROUP BY submission_type
#                     """, (st.session_state.user_id,))
#                     results = cur.fetchall()
                    
#                     if results:
#                         st.write("**Completed Challenges:**")
#                         for row in results:
#                             st.progress(row[1] % 10, text=f"{row[0]}: {row[1]} challenges")
#                     else:
#                         st.info("No completed challenges yet")
                    
#                     # Current progress
#                     st.write("**Current Progress:**")
#                     cur.execute("""
#                         SELECT 'Linux' as path, current_stage 
#                         FROM code_p_linux_progress 
#                         WHERE user_id = %s
#                         UNION ALL
#                         SELECT 'Programming' as path, current_stage 
#                         FROM code_p_programming_progress 
#                         WHERE user_id = %s
#                         UNION ALL
#                         SELECT 'Qwasar' as path, current_stage 
#                         FROM code_p_qwasar_progress 
#                         WHERE user_id = %s
#                     """, (st.session_state.user_id, st.session_state.user_id, st.session_state.user_id))
#                     progress = cur.fetchall()
                    
#                     if progress:
#                         for path, stage in progress:
#                             st.write(f"- {path}: Stage {stage + 1}")
#                     else:
#                         st.info("No active progress in any path")
                        
#             except Exception as e:
#                 st.error(f"Progress load failed: {str(e)}")
#             finally:
#                 release_db_conn(conn)
                
#             # System check button
#             if st.button("🔍 Run System Check"):
#                 with st.expander("System Diagnostics", expanded=True):
#                     # PostgreSQL check
#                     try:
#                         test_conn = get_db_conn()
#                         st.success("✅ PostgreSQL: Connection successful")
#                         release_db_conn(test_conn)
#                     except Exception as e:
#                         st.error(f"❌ PostgreSQL: Connection failed - {str(e)}")
                    
#                     # Azure check
#                     try:
#                         container_client.get_container_properties()
#                         st.success("✅ Azure Blob: Connection successful")
#                     except Exception as e:
#                         st.error(f"❌ Azure Blob: Connection failed - {str(e)}")
                    
#                     # AI check
#                     try:
#                         model.generate_content("Test connection")
#                         st.success("✅ AI Service: Connection successful")
#                     except Exception as e:
#                         st.error(f"❌ AI Service: Connection failed - {str(e)}")
#         else:
#             try:
#                 # Load progress if not loaded
#                 if 'loaded_progress' not in st.session_state:
#                     if st.session_state.learning_path == "Linux":
#                         stage, data = load_progress(st.session_state.user_id, "linux")
#                         st.session_state.linux_stage = stage
#                         st.session_state.linux_data = validate_linux_data(data)
#                     elif st.session_state.learning_path == "Programming":
#                         stage, data = load_progress(st.session_state.user_id, "programming")
#                         st.session_state.programming_stage = stage
#                         st.session_state.programming_data = validate_programming_data(data)
#                     elif st.session_state.learning_path == "Qwasar":
#                         stage, data = load_progress(st.session_state.user_id, "qwasar")
#                         # Merge loaded data with defaults
#                         full_data = validate_qwasar_data(data)
#                         st.session_state.qwasar_stage = stage
#                         st.session_state.qwasar_data = full_data
#                         # st.session_state.qwasar_data = validate_qwasar_data(data)
                        
#                         # Initialize solutions if empty
#                         if not st.session_state.qwasar_data["solutions"]:
#                             st.session_state.qwasar_data["solutions"] = [
#                                {"solution": "", "results": {}}
#                                for _ in st.session_state.qwasar_data["questions"]
#                              ]
#                     st.session_state.loaded_progress = True

#                 # Auto-save progress
#                 if st.session_state.learning_path == "Linux":
#                     save_progress(
#                         st.session_state.user_id,
#                         "linux",
#                         st.session_state.linux_stage,
#                         st.session_state.linux_data
#                     )
#                     linux_path()
#                 elif st.session_state.learning_path == "Programming":
#                     save_progress(
#                         st.session_state.user_id,
#                         "programming",
#                         st.session_state.programming_stage,
#                         st.session_state.programming_data
#                     )
#                     programming_path()
#                 elif st.session_state.learning_path == "Qwasar":
#                     save_progress(
#                         st.session_state.user_id,
#                         "qwasar",
#                         st.session_state.qwasar_stage,
#                         st.session_state.qwasar_data
#                     )
#                     qwasar_path()

#                 # Universal navigation
#                 st.markdown("---")
#                 col1, col2 = st.columns([1, 3])
#                 with col1:
#                     if st.button("🏠 Return to Path Selection"):
#                         st.session_state.learning_path = None
#                         st.session_state.pop('loaded_progress', None)
#                         st.rerun()
#                 with col2:
#                     if st.session_state.learning_path == "Linux":
#                         st.write(f"Current Linux Stage: {st.session_state.linux_stage + 1}")
#                     elif st.session_state.learning_path == "Programming":
#                         st.write(f"Current Programming Stage: {st.session_state.programming_stage + 1}")
#                     elif st.session_state.learning_path == "Qwasar":
#                         st.write(f"Current Qwasar Stage: {st.session_state.qwasar_stage + 1}")

#             except Exception as e:
#                 st.error(f"""
#                     **Progress Error**: {str(e)}
#                     - The system has reset your progress state
#                     - Your previous work has been saved
#                     - Please continue from where you left off
#                 """)
#                 st.session_state.learning_path = None
#                 st.session_state.pop('loaded_progress', None)
#                 st.rerun()

# # Entry Point with Admin Check
# if __name__ == "__main__":
#     if os.getenv("ADMIN_MODE", "false").lower() == "true":
#         admin_panel()
#     else:
#         main()




         
