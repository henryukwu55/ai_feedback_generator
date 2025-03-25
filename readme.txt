TO RUN THIS APP:

       ==> streamlit run app.py


To clear databases (azure blob and postresSQL)

      ==> python delete_all_data.py









#================================================================================
This code implements a comprehensive AI-powered grading system integrated with Canvas LMS. Here's a detailed breakdown of its functionality:

1. System Architecture:

Frontend: Streamlit web interface
Storage: Azure Blob Storage for files + PostgreSQL for metadata
AI: OpenAI GPT-3.5-turbo for grading
Integration: Canvas LMS API


2. Core Workflow:

A. Initialization & Setup
Configures Streamlit UI with custom styling and branding
Establishes connections to:
Azure Blob Storage (for file storage)
PostgreSQL (for submission metadata)
Canvas API (through custom wrapper)
OpenAI API

B. Submission Management

Canvas Integration:
Fetches course assignments and submissions using Canvas API
Handles pagination for large datasets

File Processing:
Downloads student submissions (DOCX/TXT files)
Sanitizes filenames for storage
Stores files in Azure Blob Storage

Metadata Tracking:
Records submission details in PostgreSQL:
Course/Assignment IDs
Student IDs
File locations
Timestamps

C. Authentication & Access Control

Implements email-based authentication:
Restricted to approved @amsterdam.tech accounts
24-hour access cooldown period
Tracks access times using local JSON file
Validates Canvas and OpenAI credentials

D. Grading Interface

Submission Selection:
Course → Assignment → Student hierarchy
Dynamic dropdowns populated from PostgreSQL

File Preview:
Direct access to Azure-stored files
Supports DOCX and TXT formats

AI Grading:
Custom prompt engineering for consistent feedback
Structured response parsing (Grade/Feedback/Suggestions)
Results stored in session state for export

E. Feedback Management
Rubric System:
Default rubric provided
Editable text area for custom rubrics

Comment Submission:
Integration with Canvas API for feedback delivery
Supports text and file comments

3. Key Features:

Automatic submission archiving
Grade tracking history
Excel report generation
Responsive UI with visual feedback
Error handling for API failures
Pagination handling for large Canvas datasets

4. Security Measures:

Environment variables for credentials
Input sanitization
Access time restrictions
Domain-specific authorization
Secure Azure connection strings

5. Data Flow:

Canvas → Azure/PostgreSQL (Submission collection)
Azure → Streamlit (File retrieval)
OpenAI → Streamlit (AI analysis)
Streamlit → Canvas (Feedback submission)

6. Error Handling:

Canvas API error detection
File format validation
OpenAI response parsing safeguards
Connection error checking for storage services
User input validation

7. Custom Components:

CanvasAPI class wrapping Canvas operations
AI response parser with regex safeguards
Pagination handler for Canvas API
Custom file type processors (DOCX/TXT)

8. Usage Restrictions:

Limited to approved email addresses
24-hour access window enforcement
Mentor approval requirements (as per UI notes)
Grading policy compliance reminders


9. PostgreSQL Table Creation
First, create a new table in your PostgreSQL database:
CREATE TABLE IF NOT EXISTS users (
    email VARCHAR PRIMARY KEY,
    password VARCHAR NOT NULL,
    role VARCHAR NOT NULL
);


CREATE TABLE users (
    email VARCHAR PRIMARY KEY,
    password VARCHAR NOT NULL,
    role VARCHAR NOT NULL,
    is_approved BOOLEAN DEFAULT FALSE,
    student_id VARCHAR  -- Ensure this column exists
);