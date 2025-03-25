# auth/authentication.py
import streamlit as st
from database.connection import get_db_connection
from utils.security import hash_password, is_valid_email, get_all_users, validate_user, register_user
from utils.session import save_session

# Function to render login form
def login_page():
    # Override text_input label color to black
    st.markdown(
        """
        <style>
        .stTextInput label {
            color: white !important;
        }
        </style>
        """,
        unsafe_allow_html=True
    )
    
    st.markdown("<h1 style='color:White;'>User Login</h1>", unsafe_allow_html=True)
    
    with st.form("login_form"):
        user_email = st.text_input("Email Address")
        user_password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Login")

        if submitted:
            if not user_email or not user_password:
                st.error("Please enter both email and password")
                return
                
            role, student_id = validate_user(user_email, user_password)
            if role:
                session_id = save_session(user_email, role)
                
                st.session_state.logged_in = True
                st.session_state.username = user_email
                st.session_state.role = role
                st.session_state.session_id = session_id
                st.session_state.student_id = student_id
                
                st.success("Login successful!")
                st.rerun()
            else:
                st.error("Invalid email or password")


# Function to render registration form
# def registration_page():
    
#     # Override text_input label color to black
#     st.markdown(
#         """
#         <style>
#         .stTextInput label {
#             color: white !important;
#         }
#         </style>
#         """,
#         unsafe_allow_html=True
#     )
    
#     # st.title("User Registration")
#     st.markdown("<h1 style='color:White;'>User Registration</h1>", unsafe_allow_html=True)
    
#     with st.form("registration_form"):
#         new_email = st.text_input("Email Address")
#         new_password = st.text_input("Password", type="password")
#         new_role = st.selectbox("Select Your Role", options=["admin", "instructor", "student"])
#         submitted = st.form_submit_button("Register")

#         if submitted:
#             if not new_email or not new_password:
#                 st.error("Please enter both email and password")
#                 return
            
#             success, message = register_user(new_email, new_password, new_role)
#             if success:
#                 st.success(message)
#             else:
#                 st.error(message)



def registration_page():
    st.markdown(
        """
        <style>
        /* Force text input labels to be white */
        .stTextInput label, .stSelectbox label {
            color: white !important;
        }

        /* Style error and success messages */
        .error-message {
            background-color: #FFCDD2; /* Light red */
            color: #B00020; /* Darker red */
            padding: 10px;
            border-radius: 5px;
        }

        .success-message {
            background-color: #C8E6C9; /* Light green */
            color: #2E7D32; /* Dark green */
            padding: 10px;
            border-radius: 5px;
        }

        /* Set background color for inputs to contrast with white labels */
        .stTextInput div div input, .stSelectbox div div select {
            background-color: #333333 !important; /* Dark gray input field */
            color: white !important; /* White text */
            border-radius: 5px;
            padding: 5px;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    st.markdown("<h1 style='color:White;'>User Registration</h1>", unsafe_allow_html=True)

    with st.form("registration_form"):
        new_email = st.text_input("Email Address")
        new_password = st.text_input("Password", type="password")
        new_role = st.selectbox("Select Your Role", options=["admin", "instructor", "student"])
        submitted = st.form_submit_button("Register")

        if submitted:
            if not new_email or not new_password:
                st.markdown("<div class='error-message'>Please enter both email and password</div>", unsafe_allow_html=True)
                return

            success, message = register_user(new_email, new_password, new_role)
            if success:
                st.markdown(f"<div class='success-message'>{message}</div>", unsafe_allow_html=True)
            else:
                st.markdown(f"<div class='error-message'>{message}</div>", unsafe_allow_html=True)






# def registration_page():
#     # Override text_input label color dynamically
#     st.markdown(
#         """
#         <style>
#         /* Force label color to black in light mode, white in dark mode */
#         .stTextInput label, .stSelectbox label {
#             color: black !important;
#         }

#         /* For dark mode */
#         @media (prefers-color-scheme: dark) {
#             .stTextInput label, .stSelectbox label {
#                 color: white !important;
#             }
#         }

#         /* Style error and success messages */
#         .error-message {
#             background-color: #FFCDD2; /* Light red */
#             color: #B00020; /* Darker red */
#             padding: 10px;
#             border-radius: 5px;
#         }

#         .success-message {
#             background-color: #C8E6C9; /* Light green */
#             color: #2E7D32; /* Dark green */
#             padding: 10px;
#             border-radius: 5px;
#         }
#         </style>
#         """,
#         unsafe_allow_html=True
#     )

#     st.markdown("<h1 style='color:White;'>User Registration</h1>", unsafe_allow_html=True)

#     with st.form("registration_form"):
#         new_email = st.text_input("Email Address")
#         new_password = st.text_input("Password", type="password")
#         new_role = st.selectbox("Select Your Role", options=["admin", "instructor", "student"])
#         submitted = st.form_submit_button("Register")

#         if submitted:
#             if not new_email or not new_password:
#                 st.markdown("<div class='error-message'>Please enter both email and password</div>", unsafe_allow_html=True)
#                 return

#             success, message = register_user(new_email, new_password, new_role)
#             if success:
#                 st.markdown(f"<div class='success-message'>{message}</div>", unsafe_allow_html=True)
#             else:
#                 st.markdown(f"<div class='error-message'>{message}</div>", unsafe_allow_html=True)






