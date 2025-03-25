# pages/Coding_Dashboard.py

import streamlit as st
import os
import json
from database.operations import (
    get_code_questions,
    save_code_submission,
    get_code_rubric
)
from database.connection import get_db_connection2
from utils.session import restrict_access
import google.generativeai as genai

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure Gemini Pro
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    st.error("GOOGLE_API_KEY not found in .env file")
    st.stop()
    
genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-1.5-pro-latest')

# Configure Gemini
# genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
# model = genai.GenerativeModel('gemini-pro')

def coding_academy_page():
    st.title("🏫 Code Academy")
    restrict_access(allowed_roles=['student', 'instructor'])
    
    # Session state initialization
    if 'current_code' not in st.session_state:
        st.session_state.current_code = {}
    
    # Database connection
    conn = get_db_connection2()
    
    # Layout columns
    col1, col2 = st.columns([1, 3])
    
    with col1:
        st.subheader("Question Selection")
        
        # Difficulty selector
        difficulty = st.selectbox(
            "Select Difficulty",
            ["Beginner", "Intermediate", "Advanced"],
            index=0
        )
        
        # Question selector
        questions = get_code_questions(difficulty)
        question_titles = [q[1] for q in questions]
        selected_question = st.selectbox(
            "Select Question",
            question_titles
        )
        
        # Get full question details
        question_details = next(q for q in questions if q[1] == selected_question)
        
        if st.button("Load Question"):
            st.session_state.current_question = question_details
            st.rerun()
            
        st.markdown("---")
        st.subheader("Question Details")
        if 'current_question' in st.session_state:
            st.markdown(f"**Description:** {st.session_state.current_question[2]}")
            st.markdown(f"**Expected Output:** `{st.session_state.current_question[3]}`")
            st.markdown(f"**Constraints:** {st.session_state.current_question[4]}")

    with col2:
        st.subheader("Code Editor")
        
        # File uploader
        uploaded_files = st.file_uploader(
            "Upload your solution files",
            type=["py", "js", "tsx", "html", "css"],
            accept_multiple_files=True
        )
        
        # Display uploaded files
        if uploaded_files:
            st.write("Uploaded Files:")
            for file in uploaded_files:
                st.code(f"{file.name}\n{file.getvalue().decode()}", 
                        language=file.name.split('.')[-1])
                
        # Evaluation button
        if st.button("🚀 Evaluate Code") and uploaded_files:
            with st.spinner("Analyzing code..."):
                try:
                    # Get rubric
                    rubric = get_code_rubric(st.session_state.current_question[0])
                    
                    # Prepare prompt for Gemini
                    prompt = f"""
                    Analyze this code submission against the following rubric:
                    {json.dumps(rubric, indent=2)}
                    
                    Code Files:
                    {[{"name": f.name, "content": f.getvalue().decode()} for f in uploaded_files]}
                    
                    Provide detailed feedback in JSON format with:
                    - score (0-100)
                    - strengths
                    - weaknesses
                    - improvements
                    - rubric_compliance
                    """
                    
                    # Get Gemini analysis
                    response = model.generate_content(prompt)
                    feedback = json.loads(response.text)
                    
                    # Save submission
                    save_code_submission(
                        user_id=st.session_state.username,
                        question_id=st.session_state.current_question[0],
                        files=[f.name for f in uploaded_files],
                        feedback=feedback
                    )
                    
                    # Display results
                    st.subheader("Evaluation Results")
                    st.metric("Overall Score", f"{feedback['score']}/100")
                    
                    with st.expander("Detailed Feedback"):
                        st.write("Strengths:")
                        st.write(feedback['strengths'])
                        
                        st.write("Areas for Improvement:")
                        st.write(feedback['improvements'])
                        
                        st.write("Rubric Compliance:")
                        st.json(feedback['rubric_compliance'])
                        
                except Exception as e:
                    st.error(f"Evaluation failed: {str(e)}")



# Add these functions to database/operations.py:

