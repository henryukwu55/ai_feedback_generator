# app.py
# maroon color is #800000
# light red is #FF474C
# very dark red is #581845
# dark grey is #A9A9A9 
# creme color is #FFFDD0

import streamlit as st
import pandas as pd
from auth.authentication import login_page, registration_page
from utils.session import initialize_session, set_user_session, clear_session

# Streamlit UI Configuration
# st.set_page_config(page_title="Atech SmartAssess", page_icon="📝", layout="wide")
st.set_page_config(page_title="Atech SmartAssess", page_icon="📝", layout="wide", initial_sidebar_state="expanded")

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
            
            /* Dark mode focus states */
            .stTextArea textarea:focus,
            .stTextInput input:focus,
            .stNumberInput input:focus {
                border-color: #4A90E2 !important;
                box-shadow: 0 0 0 0.2rem rgba(74, 144, 226, 0.25) !important;
            }
        </style>
    """, unsafe_allow_html=True)

# Custom CSS for other elements
st.markdown("""
    <style>
    [data-testid="stAppViewContainer"] { background: #581845; }
    
    /* Bounce animation */
    @keyframes bounce {
        0%, 100% { transform: translate(0, -50%); }
        50% { transform: translate(10px, -50%); }
    }
    
    .animated-arrow {
        position: fixed;
        top: 50%;
        left: 0;
        transform: translate(-100%, -50%);
        font-size: 3rem;
        color: #ff4b4b;
        animation: bounce 1s infinite;
        z-index: 1000;
    }
    
    /* Card styling */
    .custom-card {
        border: 4px solid #ccc;
        padding: 10px;
        border-radius: 5px;
        background-color: rgba(255, 255, 255, 0.9);
        margin-bottom: 1rem;
    }
    
    /* Dark mode card adjustment */
    @media (prefers-color-scheme: dark) {
        .custom-card {
            background-color: rgba(45, 45, 45, 0.9);
            color: white;
        }
    }
    </style>
    
    <div class="animated-arrow" title="Click the sidebar for the grading tool!">⬅️</div>
""", unsafe_allow_html=True)

# Main header
# Initialize session state
initialize_session()


from database.operations import get_admin_metrics
import random
# Replace the main header section with this conditional code
if st.session_state.logged_in:  
    pass 
    # if st.session_state.role == "admin":
    #     st.markdown("""
    #         <div style="background-color:#581845; padding:20px; border-radius:10px; margin-bottom:2rem;">
    #             <h2 style="color:#FFFDD0;">🛠️ Administration Dashboard</h2>
    #         </div>
    #     """, unsafe_allow_html=True)

    #     # First Row: Key Metrics
    #     metrics = get_admin_metrics()
    
    #     if metrics:
    #         col1, col2, col3 = st.columns(3)
    #         with col1:
    #             st.markdown(f"""
    #                 <div class="custom-card" style="background-color:#A9A9A9; padding:15px; border-radius:10px;">
    #                     <h4 style="color:#581845;">👥 Total Users</h4>
    #                     <h1 style="color:#800000;">{metrics['total_users']}</h1>
    #                     <p style="font-size:12px;">Registered users</p>
    #                 </div>
    #             """, unsafe_allow_html=True)
        
    #         with col2:
    #             st.markdown(f"""
    #                 <div class="custom-card" style="background-color:#A9A9A9; padding:15px; border-radius:10px;">
    #                     <h4 style="color:#581845;">📝 Assignments Graded</h4>
    #                     <h1 style="color:#800000;">{metrics['graded_assignments']}</h1>
    #                     <p style="font-size:12px;">Total assessments</p>
    #                 </div>
    #             """, unsafe_allow_html=True)

    #         with col3:
    #             st.markdown(f"""
    #                 <div class="custom-card" style="background-color:#A9A9A9; padding:15px; border-radius:10px;">
    #                     <h4 style="color:#581845;">📚 Active Courses</h4>
    #                     <h1 style="color:#800000;">{metrics['active_courses']}</h1>
    #                     <p style="font-size:12px;">Current courses</p>
    #                 </div>
    #             """, unsafe_allow_html=True)

    #     else:
    #         st.error("Failed to load dashboard metrics. Please check database connection.")
       




#     else:
#         st.markdown("""
#             <div style="background-color:#36454F; padding:20px; border-radius:10px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
#                 <h4 style="color: gold">Amsterdam Tech's SmartAssess</h4>
#                 <p> <b style="color: #FFFDD0;">Welcome to SmartAssess! Empowering Excellence, One Assignment at a Time!...</b> </p>
#             </div>
#         """, unsafe_allow_html=True)
# else:
#     st.markdown("""
#         <div style="background-color:#36454F; padding:20px; border-radius:10px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
#             <h4 style="color: gold">Amsterdam Tech's SmartAssess</h4>
#             <p> <b style="color: #FFFDD0;">Welcome to SmartAssess! Empowering Excellence, One Assignment at a Time!...</b> </p>
#         </div>
#     """, unsafe_allow_html=True)








# # Initialize session state
# initialize_session()

# Main application logic
if st.session_state.logged_in:
    st.sidebar.success(f"You Logged in as: {st.session_state.username}, {st.session_state.role}")
    st.sidebar.button("🚪 Logout", on_click=lambda: st.session_state.update(logged_in=False))
    
#    if st.session_state.role == "admin":
# #       pass  
    if st.session_state.role == "admin":
        st.markdown("""
            <div style="background-color:#581845; padding:20px; border-radius:10px; margin-bottom:2rem;">
                <h2 style="color:#FFFDD0;">🛠️ Administration Dashboard</h2>
            </div>
        """, unsafe_allow_html=True)

        # First Row: Key Metrics
        metrics = get_admin_metrics()
    
        if metrics:
            col1, col2, col3 = st.columns(3)
            with col1:
                st.markdown(f"""
                    <div class="custom-card" style="background-color:#A9A9A9; padding:15px; border-radius:10px;">
                        <h4 style="color:#581845;">👥 Total Users</h4>
                        <h1 style="color:#800000;">{metrics['total_users']}</h1>
                        <p style="font-size:12px;">Registered users</p>
                    </div>
                """, unsafe_allow_html=True)
        
            with col2:
                st.markdown(f"""
                    <div class="custom-card" style="background-color:#A9A9A9; padding:15px; border-radius:10px;">
                        <h4 style="color:#581845;">📝 Assignments Graded</h4>
                        <h1 style="color:#800000;">{metrics['graded_assignments']}</h1>
                        <p style="font-size:12px;">Total assessments</p>
                    </div>
                """, unsafe_allow_html=True)

            with col3:
                st.markdown(f"""
                    <div class="custom-card" style="background-color:#A9A9A9; padding:15px; border-radius:10px;">
                        <h4 style="color:#581845;">📚 Active Courses</h4>
                        <h1 style="color:#800000;">{metrics['active_courses']}</h1>
                        <p style="font-size:12px;">Current courses</p>
                    </div>
                """, unsafe_allow_html=True)

        else:
            st.error("Failed to load dashboard metrics. Please check database connection.")



        # Second Row: Main Content
        col_left, col_right = st.columns([2, 1])
    
        with col_left:
            # with st.expander("📈 System Activity Monitor", expanded=True):
            #     st.markdown("""
            #         <div style="background-color:#A9A9A9; padding:15px; border-radius:5px;">
            #             <h5 style="color:#581845;">Real-time Grading Activity</h5>
            #             <!-- Placeholder for activity graph -->
            #             <div style="height:200px; background-color:#FFFDD0; border-radius:5px; padding:10px;">
            #                 <p style="color:#581845;">Activity Graph Area</p>
            #             </div>
            #         </div>
            #     """, unsafe_allow_html=True)
                
            from database.connection import get_db_connection
            with st.expander("📈 System Activity Monitor", expanded=True):
                conn = get_db_connection()
                try:
                   with conn.cursor() as cursor:
                     cursor.execute("""
                         SELECT DATE(timestamp) as day, COUNT(*) 
                         FROM grading_records 
                         GROUP BY day 
                         ORDER BY day DESC 
                         LIMIT 7
                     """)
                     data = cursor.fetchall()
                     df = pd.DataFrame(data, columns=['Date', 'Submissions'])
                     st.line_chart(df.set_index('Date'))
                except Exception as e:
                     st.error(f"Error loading activity data: {str(e)}")
                finally:
                     conn.close()    

 
            with st.expander("🔐 User Management", expanded=True):
                # st.markdown("""
                #     <div style="background-color:#A9A9A9; padding:15px; border-radius:5px;">
                #         <div style="display:flex; justify-content:space-between; margin-bottom:15px;">
                #             <input type="text" placeholder="Search users..." style="width:60%; padding:5px;">
                #             <button style="background-color:#581845; color:white; border:none; padding:5px 10px;">Add User</button>
                #         </div>
                #         <!-- User table placeholder -->
                #         <div style="height:200px; background-color:#FFFDD0; border-radius:5px; padding:10px;">
                #             <p style="color:#581845;">User Table Area</p>
                #         </div>
                #     </div>
                # """, unsafe_allow_html=True)
                
            # with st.expander("🔐 User Management", expanded=True):
                conn = get_db_connection()
                try:
                    with conn.cursor() as cursor:
                       search_query = st.text_input("Search users...")
                       query = """
                            SELECT is_approved, email, role, created_at 
                            FROM users 
                            WHERE email LIKE %s 
                            ORDER BY created_at DESC
                        """
                       cursor.execute(query, (f'%{search_query}%',))
                       users = cursor.fetchall()
            
                       if users:
                            df = pd.DataFrame(users, columns=['is_approved', 'Email', 'Role', 'Created At'])
                            st.dataframe(df.style.format({
                                 'Created At': lambda x: x.strftime('%Y-%m-%d %H:%M') if not pd.isnull(x) else ''
                            }))
                       else:
                           st.warning("No users found")
                except Exception as e:
                     st.error(f"Error loading users: {str(e)}")
                finally:
                     conn.close()      
                
                
                

        with col_right:
            st.markdown("""
                <div style="background-color:#A9A9A9; padding:15px; border-radius:10px;">
                    <h4 style="color:#581845;">📋 Quick Actions</h4>
                    <button style="background-color:#581845; color:white; border:none; padding:5px 10px; margin:5px;">Audit Logs</button>
                    <button style="background-color:#581845; color:white; border:none; padding:5px 10px; margin:5px;">System Config</button>
                    <button style="background-color:#581845; color:white; border:none; padding:5px 10px; margin:5px;">Backup Now</button>
                </div>
            """, unsafe_allow_html=True)

        # Third Row: System Health
        with st.expander("⚙️ System Health Dashboard", expanded=True):
            st.markdown("""
                <div style="background-color:#A9A9A9; padding:15px; border-radius:5px;">
                    <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 15px;">
                        <div style="background-color:#FFFDD0; padding:10px; border-radius:5px;">
                            <h5 style="color:#581845;">API Response Time</h5>
                            <p style="color:#800000;">142ms avg</p>
                        </div>
                        <div style="background-color:#FFFDD0; padding:10px; border-radius:5px;">
                            <h5 style="color:#581845;">Database Load</h5>
                            <p style="color:#800000;">34% capacity</p>
                        </div>
                        <div style="background-color:#FFFDD0; padding:10px; border-radius:5px;">
                            <h5 style="color:#581845;">AI Model Accuracy</h5>
                            <p style="color:#800000;">92.4%</p>
                        </div>
                    </div>
                </div>
            """, unsafe_allow_html=True)   

    
    else:    
        # Video section
        # with open(r"C:\Users\Henry Ukwu\Desktop\Gradquest\assets\Student Town Hall March 2023.mp4", "rb") as video_file:
        with open(r"C:\Users\Henry Ukwu\Desktop\Gradquest\assets\streamlit-Home-2025-03-22-14-03-64.webm", "rb") as video_file:
            video_bytes = video_file.read()
        st.video(video_bytes)
        # st.markdown("#### Video Details:")
        st.markdown("""<div>
                    <p style="color: white;"> <b> Video Details: </b> </p>
                    </div>""", unsafe_allow_html=True)
        # st.write("This video demonstrates how students can retrieve their assignments from Canvas LMS and evaluate them using the ATech SmartAssess app.")
        st.markdown("""<p style="color: white;">
                    This video demonstrates how students can retrieve their assignments from Canvas LMS and evaluate them using the ATech SmartAssess app.
                  </p>""", unsafe_allow_html=True)
        st.markdown("<br><br><br><br>", unsafe_allow_html=True)  # Adds two line breaks for spacing
        # Columns with cards
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(""" 
                <div class="custom-card" style="background-color:#A9A9A9; padding:20px; border-radius:10px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                    <h2>Code of the Day</h2>
                    <p>Today's tip: Discover how list comprehensions can simplify your code.</p>
                </div>
            """, unsafe_allow_html=True)
            st.code("[x for x in range(10) if x % 2 == 0]", language="python")

        with col2:
            pass
        
            # method 3 ===========================
            st.markdown("""
               <div class="custom-card" style="background-color:#A9A9A9; padding:20px; border-radius:10px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); line-height: 1;">
                   <h5 style="color: #581845; margin-bottom: 15px;">📚 Ethical Guidelines</h5>
                   <h6> 1. Academic Integrity Principles </h6>
                   <p> Ethical Use: Treat AI feedback as a learning aid, not an answer key</p>
                   <p> Unethical: Copying AI suggestions verbatim without understanding</p>
                   <p> Example: Use feedback to improve arguments, not rewrite entire assignment</p>
                   <p> Maintain 80%+ original content after implementing AI suggestions</p>
                   <p> Always add personal analysis/interpretations </p>             
                   <h6> 2. Transparency</h6>
                   <p> Disclose AI use in submissions</p>
                   <p> Keep revision history showing human-AI collaboration</p>               
                   <h6> 3. Responsible Engagement </h6>
                   <p> Critical Evaluation - Verify against:</p> 
                   <p> - Course materials </p>
                   <p> - Rubric criteria </p>
                   <p> - Personal knowledge </p>
                   <p> Bias Awareness: </p>
                   <p> - Example: If AI suggests "use more complex words" but your facilitator emphasizes clarity, question the feedback </p>               
                   <h6> 4. Privacy Protection - Never submit confidential/sensitive content unless the tool has: </h6>
                   <p> - Enterprise-grade encryption </p>
                   <p> - Clear data retention policies </p>               
                   <h6> 5. Healthy Usage </h6>
                   <p> ⏱️ Limit to 30-45min/session to prevent over-reliance</p>
                   <p> 🧠 Schedule "AI-free" critical thinking periods </p>
                   <p> ⚠️ Error Reporting - Flag questionable feedback </p>
                 
                </div>
                  """, unsafe_allow_html=True)
        
        
    
        with col3:
           st.markdown("""
             <div class="custom-card" style="background-color:#A9A9A9; padding:20px; border-radius:10px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                <h2>Coding Challenge</h2>
                <p>
                   Coding Challenge: Join our data cleaning exercise! Your task is to improve the efficiency of a script that cleans a messy student performance dataset. Identify issues, propose solutions, and share your approach.
                </p>
                <a href="https://vscode.dev" target="_blank">
                    <button style="padding: 10px; font-size:16px;">Join the Challenge</button>
                </a>
             </div>
            """, unsafe_allow_html=True)    
        
else:
    page = st.sidebar.radio("Navigation", ["Login", "Register"])
    if page == "Login":
        login_page()
    else:
        registration_page()    

# else:
#     page = st.sidebar.radio("Navigation", ["Login", "Register"])
#     login_page() if page == "Login" else registration_page()


# Sticky footer
st.markdown("""
    <style>
    .footer {
        position: fixed;
        left: 0;
        bottom: 0;
        width: 100%;
        background-color: #f8f8f8;
        color: #333333;
        text-align: center;
        padding: 2px;
        z-index: 100;
    }
    </style>
    <div class="footer">
        <p>Powered by ATech Faculty | &copy; 2025 Amsterdam Tech AI Innovations Team</p>
    </div>
""", unsafe_allow_html=True)





