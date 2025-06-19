# database/connection.py
import psycopg2
import os
from dotenv import load_dotenv
import streamlit as st
import json

load_dotenv()

# Database Configuration
DB_CONFIG = {
    "host": os.getenv("POSTGRESQL_HOST"),
    "database": os.getenv("POSTGRESQL_DATABASE"),
    "user": os.getenv("POSTGRESQL_USER"),
    "password": os.getenv("POSTGRESQL_PASSWORD"),
}

# Function to establish database connection
def get_db_connection():
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        return conn
    except Exception as e:
        st.error(f"Database connection failed: {e}")
        return None
    
    
#=================================

DATABASE_CONFIG = {
    "host": os.getenv("POSTGRESQL_HOST"),
    "database": os.getenv("DB_DATABASE"),
    "user": os.getenv("POSTGRESQL_USER"),
    "password": os.getenv("POSTGRESQL_PASSWORD"),
}


def get_db_connection2():
    try:
        conn = psycopg2.connect(**DATABASE_CONFIG)
        return conn
    except Exception as e:
        st.error(f"Database connection failed: {e}")
        return None



def get_code_questions(difficulty):
    conn =  get_db_connection2()
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT id, title, description, expected_output, constraints 
                FROM code_questions 
                WHERE difficulty = %s
            """, (difficulty,))
            return cursor.fetchall()
    finally:
        conn.close()

def get_code_rubric(question_id):
    conn =  get_db_connection2()
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT rubric FROM code_questions 
                WHERE id = %s
            """, (question_id,))
            return cursor.fetchone()[0]
    finally:
        conn.close()

def save_code_submission(user_id, question_id, files, feedback):
    conn =  get_db_connection2()
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                INSERT INTO code_submissions 
                (user_id, question_id, files, feedback)
                VALUES (%s, %s, %s, %s)
            """, (user_id, question_id, json.dumps(files), json.dumps(feedback)))
            conn.commit()
    finally:
        conn.close()
        
        
