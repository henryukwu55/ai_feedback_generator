import streamlit as st

st.markdown("# 🚧 Page Under Construction 🚧")
st.markdown("### This feature is coming soon. Stay tuned!")




# This implementation includes:
# Full stage progression system with session state tracking
# Integrated Qwasar platform interface
# Recruitment agency partnerships with real logos
# Document management system (CV/LinkedIn/GitHub)
# Coaching scheduling with calendar integration
# Job application tracking pipeline
# Continuous support resources
# Interactive checklists for stage completion
# Partner company integrations
# Responsive layout with progress visualization
# Error handling and form validation
# Lottie animations for key transitions


# import streamlit as st
# from streamlit_lottie import st_lottie
# import requests
# from datetime import datetime, timedelta

# # Configuration
# st.set_page_config(
#     page_title="Amsterdam Tech TAP Portal",
#     page_icon="🚀",
#     layout="wide"
# )

# # Lottie Animations
# TAP_ANIMATION = "https://assets10.lottiefiles.com/packages/lf20_qp1q7mct.json"
# # SUCCESS_ANIMATION = "https://assets9.lottiefiles.com/packages/lf20_8wRE4I.json"
# SUCCESS_ANIMATION = "https://assets10.lottiefiles.com/packages/lf20_qp1q7mct.json"

# # Session State Initialization
# if 'current_stage' not in st.session_state:
#     st.session_state.current_stage = 0
# if 'completed' not in st.session_state:
#     st.session_state.completed = {
#         'stage1': False,
#         'stage2': False,
#         'stage3': False
#     }
# if 'bookings' not in st.session_state:
#     st.session_state.bookings = []

# # Load Animations
# @st.cache_data
# def load_lottie(url):
#     r = requests.get(url)
#     return r.json() if r.status_code == 200 else None

# # Custom CSS
# st.markdown("""
# <style>
#     .stProgress > div > div > div {background-color: #87CEFA;}
#     .st-bb {background-color: #87CEEB;}
#     .st-at {background-color: #B0C4DE;}
#     .stTabs > div > div > button {font-weight: bold; color: #0070c0;}
#     .stMarkdown h2 {border-bottom: 2px solid #003082;}
# </style>
# """, unsafe_allow_html=True)

# # Header Section
# col1, col2 = st.columns([2, 3])
# with col1:
#     # st.image("https://upload.wikimedia.org/wikipedia/en/0/0f/University_of_Amsterdam_logo.svg", width=200)
#     st.image(r"C:\Users\Henry Ukwu\Desktop\Gradquest\assets\logo.png", width=200)
# with col2:
#     st.title("Talent Acceleration Programme")
#     st_lottie(load_lottie(TAP_ANIMATION), height=150, key="header_anim")

# # Progress Tracker
# def show_progress():
#     stages = [
#         "🎯 Stage 1: Career Setup", 
#         "🤝 Stage 2: Interviews", 
#         "🔁 Stage 3: Ongoing Support"
#     ]
#     progress = st.session_state.current_stage / 3
#     st.progress(progress, text=" → ".join(stages[:st.session_state.current_stage+1]))

# show_progress()

# # Main Tabs
# tab1, tab2, tab3 = st.tabs([
#     "Stage 1: Career Preparation", 
#     "Stage 2: Interview Opportunities", 
#     "Stage 3: Continuous Support"
# ])

# # Stage 1 Content
# with tab1:
#     st.header("Career Launch Preparation")
#     with st.expander("📘 Programme Overview", expanded=True):
#         st.markdown("""
#         **Stage 1 Outcomes:**
#         - ✅ Personalized career roadmap
#         - ✅ Optimized professional profiles
#         - ✅ Technical interview readiness
#         """)
    
#     col1, col2 = st.columns([3, 2])
#     with col1:
#         with st.form("stage1_form"):
#             st.subheader("Career Profile Setup")
            
#             # Document Upload
#             cv = st.file_uploader("Upload CV (PDF only)", type="pdf")
#             linkedin = st.text_input("LinkedIn Profile URL")
#             github = st.text_input("GitHub Profile URL")
            
#             # Coaching Booking
#             coaching_date = st.date_input("Book 1:1 Coaching", 
#                                        min_value=datetime.today(),
#                                        max_value=datetime.today()+timedelta(days=14))
#             coaching_time = st.selectbox("Available Slots", 
#                                        ["09:00-10:00", "11:00-12:00", "14:00-15:00"])
            
#             if st.form_submit_button("Save Profile"):
#                 if cv and linkedin:
#                     st.session_state.bookings.append({
#                         'date': coaching_date,
#                         'time': coaching_time
#                     })
#                     st.success("Profile saved! Next: Complete mock interviews")
#                 else:
#                     st.error("Missing required documents")
    
#     with col2:
#         st.subheader("Technical Preparation")
#         st.markdown("""
#         **Qwasar Platform Requirements:**
#         1. Complete 3 mock interviews
#         2. Achieve 80%+ score
#         3. Review technical feedback
#         """)
        
#         if st.button("Start Qwasar Interview"):
#             st.components.v1.iframe("https://qwasar.io", height=400)
        
#         if st.checkbox("I've completed Qwasar requirements"):
#             st.session_state.completed['stage1'] = True
#             st.session_state.current_stage = 1

# # Stage 2 Content
# with tab2:
#     if st.session_state.completed['stage1']:
#         st.header("Interview Opportunities")
        
#         # Recruitment Partners
#         st.subheader("Partner Agencies")
#         col1, col2, col3 = st.columns(3)
#         with col1:
#             st.image("https://upload.wikimedia.org/wikipedia/commons/9/91/Randstad_logo.svg", width=150)
#             st.button("Connect with Randstad")
#         with col2:
#             st.image("https://upload.wikimedia.org/wikipedia/commons/3/3a/Hays_logo.svg", width=150)
#             st.button("Connect with Hays")
#         with col3:
#             st.image("https://upload.wikimedia.org/wikipedia/commons/8/89/Michael_Page_International_logo.svg", width=150)
#             st.button("Connect with Michael Page")
        
#         # Interview Tracking
#         st.subheader("Interview Pipeline")
#         with st.expander("Active Applications"):
#             if st.button("+ Add New Application"):
#                 st.session_state.new_app = True
            
#             if 'new_app' in st.session_state:
#                 with st.form("new_application"):
#                     company = st.text_input("Company Name")
#                     role = st.text_input("Position")
#                     date = st.date_input("Interview Date")
#                     if st.form_submit_button("Track Application"):
#                         st.success(f"Added {company} application")
#                         del st.session_state.new_app
        
#         if st.checkbox("I've completed 3+ interviews"):
#             st.session_state.completed['stage2'] = True
#             st.session_state.current_stage = 2
#     else:
#         st.warning("Complete Stage 1 requirements to unlock interview opportunities")

# # Stage 3 Content
# with tab3:
#     if st.session_state.completed['stage2']:
#         st.header("Continuous Career Support")
        
#         col1, col2 = st.columns([2, 3])
#         with col1:
#             st.subheader("Support Resources")
#             st.markdown("""
#             - 🗓 Weekly Career Webinars
#             - 📈 Monthly Market Reports
#             - 👥 Alumni Networking Forum
#             - 🔄 CV Refresh Service
#             """)
            
#             st.button("Join Alumni Network")
#             st.button("Request CV Review")
        
#         with col2:
#             st.subheader("Job Search Tracker")
#             with st.form("job_tracker"):
#                 search_status = st.selectbox("Current Status", [
#                     "Actively interviewing",
#                     "Considering offers",
#                     "Exploring options"
#                 ])
#                 target_roles = st.text_input("Target Roles")
#                 geographic_pref = st.multiselect("Locations", [
#                     "Amsterdam", "Rotterdam", "Remote", 
#                     "EU-wide", "International"
#                 ])
#                 if st.form_submit_button("Update Preferences"):
#                     st.success("Tracker updated")
        
#         if st.checkbox("I'm employed and want to help others"):
#             st.session_state.completed['stage3'] = True
#             st_lottie(load_lottie(SUCCESS_ANIMATION), height=200)
#     else:
#         st.info("Complete Stage 2 to access ongoing support resources")

# # Partner Section
# st.markdown("---")
# st.subheader("Hiring Partners")

# from PIL import Image
# import os

# # Create an assets folder and add partner logos
# def get_partner_logos():
#     try:
#         return [
#             # Image.open("assets/adyen.png"),
#             Image.open("assets/aigents.png"),
#             Image.open("assets/eleven-lab.png"),
#             Image.open("assets/partner.png"),
#             # Image.open("assets/optiver.png"),
#             # Image.open("assets/databricks.png")
#         ]
#     except Exception as e:
#         st.error(f"Error loading partner logos: {e}")
#         return []
        
# # In your partner section:
# logos = get_partner_logos()
# if logos:
#     cols = st.columns(3)
#     for col, logo in zip(cols, logos):
#         with col:
#             st.image(logo, use_container_width=True)
# else:
#     st.warning("Partner logos unavailable - showing placeholder text")
#     st.write("Our partners include: Adyen | Optiver | Databricks")


# # Footer
# st.markdown("---")
# st.markdown("""
# **TAP Support Center**  
# 📞 +31 20 525 8888  
# 📧 tap-support@amsterdamtech.nl  
# 📍 Science Park 904, 1098 XH Amsterdam  
# """)





















# import streamlit as st
# from streamlit.components.v1 import html
# from streamlit_lottie import st_lottie
# import requests

# # Function to load Lottie animation from URL
# def load_lottieurl(url: str):
#     r = requests.get(url)
#     if r.status_code != 200:
#         return None
#     return r.json()

# # Load a Lottie animation (you can change the URL to another one from lottiefiles.com)
# career_lottie_url = "https://assets10.lottiefiles.com/packages/lf20_qp1q7mct.json"

# career_animation = load_lottieurl(career_lottie_url)

# # Configure page settings
# st.set_page_config(
#     page_title="Amsterdam Tech - Talent Acceleration Program",
#     page_icon="🎓",
#     layout="wide"
# )

# # Inject custom CSS
# def inject_custom_css():
#     st.markdown("""
#     <style>
#         .main {background-color: #f8f9fa;}
#         .stButton>button {width: 100%; font-weight: bold; font-size: 16px;}
#         .header {color: #003082;}  
#         .subheader {color: #0070c0; font-size: 1.2rem;}
#         .success {color: #28a745;}
#         .required:after {content: " *"; color: red;}
#     </style>
#     """, unsafe_allow_html=True)

# inject_custom_css()

# # Session state
# if 'active_form' not in st.session_state:
#     st.session_state.active_form = None

# # Amsterdam Tech logo
# st.image(r"C:\Users\Henry Ukwu\Desktop\Gradquest\assets\logo.png", width=150)

# # Page title
# st.title("Talent Acceleration Program")
# st.markdown("---")

# # Description and visuals
# col1, col2 = st.columns([3, 2])
# with col1:
#     st.subheader("Accelerate Your Tech Career")
#     st.markdown("""
#     **The Talent Acceleration Program (TAP) offers:**
#     - Industry-aligned curriculum in Software Engineering, Data Science, and AI
#     - Mentorship from leading tech professionals
#     - Career development workshops
#     - Exclusive networking opportunities
#     """)

# with col2:
#     if career_animation:
#         st_lottie(career_animation, height=300, key="tap_hero")

# # Form rendering functions
# def render_join_tap():
#     with st.form(key='join_tap_form'):
#         st.subheader("TAP Enrollment Application")
#         st.markdown('<p class="subheader">Complete the form to begin your acceleration journey</p>', unsafe_allow_html=True)

#         full_name = st.text_input("Full Name", placeholder="John Doe")
#         email = st.text_input("Email Address", placeholder="john.doe@example.com")
#         department = st.selectbox("Primary Interest Department",
#                                   ["Software Engineering", "Data Science", "Artificial Intelligence", "Machine Learning"])
#         career_status = st.selectbox("Current Professional Status",
#                                      ["Employed", "Student", "Seeking Employment", "Career Transition"])
#         motivation = st.text_area("Motivation Statement",
#                                   placeholder="Describe your professional goals and how TAP can help achieve them (500 words max)",
#                                   height=150)

#         if st.form_submit_button("Submit Application", type="primary"):
#             if full_name and email and motivation:
#                 st.session_state.active_form = None
#                 st.success("🎉 Application submitted successfully! Our admissions team will contact you within 3 business days.")
#             else:
#                 st.error("⚠️ Please complete all required fields.")

# def render_career_assessment():
#     with st.form(key='career_assessment_form'):
#         st.subheader("Career Development Assessment")
#         st.markdown('<p class="subheader">Personalized career path analysis</p>', unsafe_allow_html=True)

#         experience = st.slider("Years of Professional Experience", 0, 20, 1)
#         skills = st.multiselect("Technical Skills",
#                                 ["Python", "Machine Learning", "Cloud Computing", "Data Analysis",
#                                  "Software Architecture", "Deep Learning", "Big Data", "JavaScript", "React"])
#         goals = st.text_area("Career Objectives",
#                              placeholder="Describe your 3-5 year career goals (300 words max)",
#                              height=120)

#         if st.form_submit_button("Generate Career Plan", type="primary"):
#             st.session_state.active_form = None
#             st.success("✅ Assessment complete! Your personalized development plan will be emailed within 24 hours.")

# # Buttons with animation
# st.markdown("## 👇 Choose Your Next Step")
# st.markdown("---")

# # Show animation again above buttons
# if career_animation:
#     st_lottie(career_animation, height=250, key="career_buttons")

# col1, col2, col3 = st.columns(3)
# with col1:
#     if st.button("🚀 Join Talent Program", help="Begin your application for the TAP program"):
#         st.session_state.active_form = 'join_tap'
# with col2:
#     if st.button("📈 Career Assessment", help="Get personalized career recommendations"):
#         st.session_state.active_form = 'career_assessment'
# with col3:
#     if st.button("ℹ️ Program Information", help="View detailed program information"):
#         st.session_state.active_form = 'info'

# # Render selected form
# if st.session_state.active_form == 'join_tap':
#     render_join_tap()
# elif st.session_state.active_form == 'career_assessment':
#     render_career_assessment()
# elif st.session_state.active_form == 'info':
#     st.subheader("Program Details")
#     st.markdown("""
#     **Talent Acceleration Program Features:**
#     - Duration: 6-12 months flexible program
#     - Format: Hybrid (Online Sessions)
#     - Eligibility: Have a Bachelor's degree or equivalent experience, or be in the final year of a Bachelor's program.
#     - Certification: Amsterdam Tech Professional Certificate
    
#     **Key Dates:**
#     - Application Deadline: 15th of Each Month
#     - Program Start: 1st of Each Month
#     """)

# # Footer
# st.markdown("---")
# st.markdown("""
# **Amsterdam Tech**  
# Science Park 904 | 1098 XH Amsterdam  
# 📞 +31 (0)20 525 9111  
# ✉️ tap-admissions@amsterdam.tech  
# """)






