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








coding platform database command creation:
-- Enhanced Users Table
CREATE TABLE code_p_users (
    user_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(100),
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMPTZ,
    registration_source VARCHAR(50),
    is_verified BOOLEAN DEFAULT FALSE,
    CONSTRAINT valid_email CHECK (email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$')
);

-- Enhanced Linux Progress Tracking
CREATE TABLE code_p_linux_progress (
    progress_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES code_p_users(user_id) ON DELETE CASCADE,
    current_stage INTEGER NOT NULL DEFAULT 0,
    total_attempts INTEGER DEFAULT 0,
    total_time_spent INTERVAL,
    linux_data JSONB,
    stage_started_at TIMESTAMPTZ,
    last_updated TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMPTZ
);

-- Enhanced Programming Progress Tracking
CREATE TABLE code_p_programming_progress (
    progress_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES code_p_users(user_id) ON DELETE CASCADE,
    current_stage INTEGER NOT NULL DEFAULT 0,
    total_attempts INTEGER DEFAULT 0,
    total_time_spent INTERVAL,
    programming_data JSONB,
    stage_started_at TIMESTAMPTZ,
    last_updated TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMPTZ
);

-- Comprehensive Submissions Table
CREATE TABLE code_p_submissions (
    submission_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES code_p_users(user_id) ON DELETE CASCADE,
    submission_type VARCHAR(50) NOT NULL,
    task_project_id UUID,  -- References specific tasks/projects
    difficulty_level VARCHAR(50),
    topic VARCHAR(100),
    submission_data JSONB NOT NULL,
    evaluation_results JSONB,
    status VARCHAR(20) DEFAULT 'pending',
    submission_metadata JSONB,
    feedback_viewed BOOLEAN DEFAULT FALSE,
    revised_after_approval BOOLEAN DEFAULT FALSE,
    approved_at TIMESTAMPTZ,
    submitted_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    completion_time INTERVAL,
    CONSTRAINT valid_status CHECK (status IN ('pending', 'approved', 'rejected'))
);

-- Indexes for Analytics
CREATE INDEX idx_submissions_type ON code_p_submissions(submission_type);
CREATE INDEX idx_submissions_difficulty ON code_p_submissions(difficulty_level);
CREATE INDEX idx_submissions_topic ON code_p_submissions(topic);
CREATE INDEX idx_submissions_timestamp ON code_p_submissions(submitted_at);




-- Task/Project Catalog (for trend analysis)
CREATE TABLE code_p_tasks (
    task_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    task_type VARCHAR(50) NOT NULL,
    difficulty VARCHAR(50) NOT NULL,
    topic VARCHAR(100) NOT NULL,
    average_completion_time INTERVAL,
    success_rate DECIMAL(5,2),
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- Skill Taxonomy (for competency mapping)
CREATE TABLE code_p_skills (
    skill_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    skill_name VARCHAR(100) NOT NULL,
    category VARCHAR(50) NOT NULL,
    difficulty_level VARCHAR(50) NOT NULL,
    description TEXT
);

-- User-Skill Relationships
CREATE TABLE code_p_user_skills (
    user_id UUID REFERENCES code_p_users(user_id),
    skill_id UUID REFERENCES code_p_skills(skill_id),
    proficiency_score DECIMAL(5,2),
    last_assessed_at TIMESTAMPTZ,
    PRIMARY KEY (user_id, skill_id)
);



PRVIOUS REQUIREMENTS.TXT:
streamlit==1.43.0
python-dotenv==1.0.0
openai==0.28.0
requests==2.31.0
python-docx==0.8.11
pandas==2.2.0
azure-storage-blob==12.23.1
xlsxwriter==3.2.2
statsmodels==0.14.4
plotly==6.0.0
matplotlib==3.8.2
wordcloud==1.9.4
seaborn==0.12.2
numpy==1.26.4
psycopg2-binary==2.9.9
xlwt==1.3.0
slack-sdk==3.27.1
canvasapi==3.2.0
python-pptx==0.6.23
setuptools==69.1.0
openpyxl==3.1.5
streamlit-lottie==0.0.5
PyPDF2==3.0.1
