# pages/1_🧑‍💼_Admin_Dashboard.py
import streamlit as st
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt
from wordcloud import WordCloud
from database.operations import get_all_users, approve_user, delete_user, save_user_approvals, update_user_approvals_in_db
from database.connection import get_db_connection
from utils.session import initialize_session, restrict_access, get_active_sessions, update_activity
from utils.security import get_all_grading_data, generate_excel_report

# Configure Plotly default template
px.defaults.template = "plotly_white"
plt.style.use('ggplot')


# Add to the top of every page/script
def track_activity():
    if st.session_state.get("logged_in"):
        update_activity()


def admin_dashboard():
    # Initialize session, track activity, and access control
    track_activity()
    initialize_session()
    restrict_access(allowed_roles=['admin'])
    
    # Set page title and header
    # st.title("📊 Admin Dashboard - Analytics Center")
    
    # Load all data with caching
    @st.cache_data(ttl=300)          
    def load_data():
      return {
        'users': pd.DataFrame(
            get_all_users(), 
            columns=["email", "role", "is_approved", "created_at"]
        ).rename(columns={
            'email': 'Email',
            'role': 'Role',
            'is_approved': 'Approved',
            'created_at': 'Created At'
        }),
        'sessions': pd.DataFrame(get_active_sessions(), columns=["session_id", "user_id", "role", "login_time", "last_activity"]),
        
        'grading': pd.DataFrame(
            get_all_grading_data(),
            columns=[
                'id','course_id', 'assignment', 'student', 'file', 'grade',
                'feedback', 'suggestions', 'instructor_comment', 'timestamp'
            ]
        )
      }
   
    data = load_data()
    # Convert grade column to numeric during data loading
    data['grading']['grade'] = pd.to_numeric(
        data['grading']['grade'], 
        errors='coerce')
    
    users_df = data['users']
    sessions_df = data['sessions']
    grading_df = data['grading']

    # =====================
    # Quick Metrics Section
    # =====================
    st.subheader("📈 Key Performance Indicators")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        # pending = users_df[~users_df['is_approved']].shape[0]
        pending = users_df[~users_df['Approved']].shape[0]
        st.metric("Pending Approvals", f"{pending} Users", help="Users awaiting administrator approval")

    with col2:
        try:
            # Safely calculate average grade
            avg_grade = 0  # Default value
            if not grading_df.empty:
               # Convert grade column to numeric if needed
               grading_df['grade'] = pd.to_numeric(grading_df['grade'], errors='coerce')
               
               if 'grade' in grading_df.columns:
                   valid_grades = grading_df['grade'].dropna()
                   if not valid_grades.empty:
                      avg_grade = valid_grades.mean()
                   
            # Format output with fallbacks
            display_value = f"{avg_grade:.1f}/10" if avg_grade > 0 else "N/A"
            st.metric("Average Grade", display_value, 
                 help="Average score across valid graded assignments")
                   
        except Exception as e: 
            st.error(f"Grade calculation error: {str(e)}")
            st.metric("Average Grade", "N/A", 
                 help="Could not calculate average grade")
            
    with col3:
        try:
           # Get fresh session data
           active_sessions = pd.DataFrame(
              get_active_sessions(),  
              columns=["session_id", "user_id", "role", "login_time"] )
           active = active_sessions['user_id'].nunique()  # Count distinct users
           st.metric("Active Sessions", 
                 f"{active} Users", 
                 help="Users active in last 30 minutes")
        except Exception as e:   
           st.error(f"Session error: {str(e)}") 
           st.metric("Active Sessions", "N/A")
           
           
           

    with col4:
        feedback_ratio = grading_df.shape[0]/active if active > 0 else 0
        st.metric("Feedback Ratio", f"{feedback_ratio:.1f}:1", help="Feedback items per active session")

    # =====================
    # User Analytics Section
    # =====================
    st.header("👥 User Management Analytics")
    
    # User Approval Status
    fig1 = px.pie(users_df, names='Approved', 
                 title="User Approval Status Distribution",
                 color_discrete_sequence=px.colors.qualitative.Pastel)
    st.plotly_chart(fig1, use_container_width=True)

    # Role Distribution
    if not users_df.empty:
        role_counts = users_df['Role'].value_counts().reset_index()
        fig2 = px.bar(role_counts, x='Role', y='count',
                      title="User Role Distribution",
                      labels={'count': 'Number of Users'},
                      color='Role')
        st.plotly_chart(fig2, use_container_width=True)
        
    # Then update all references in the code:
    users_df = users_df.rename(columns={
        'email': 'Email',
        'role': 'Role',
        'is_approved': 'Approved',
        'created_at': 'Created At'
    })

    # Registration Timeline
    if 'Created At' in users_df.columns:
        users_df['Created At'] = pd.to_datetime(users_df['Created At'])
        reg_timeline = users_df.set_index('Created At').resample('M').size()
        fig3 = px.line(reg_timeline, title="Monthly User Registrations",
                       labels={'value': 'New Users', 'CreatedAt': 'Date'})
        st.plotly_chart(fig3, use_container_width=True)
   
    
    # =====================
    # Grading Analytics Section
    # =====================
    st.header("📚 Grading Performance Analytics")
    
    if not grading_df.empty:
        # Grade Distribution
        fig6 = px.histogram(grading_df, x='grade', nbins=20,
                          title="Grade Distribution Analysis",
                          color_discrete_sequence=['#2CA02C'])
        st.plotly_chart(fig6, use_container_width=True)

        # Feedback Analysis
        col1, col2 = st.columns(2)
        with col1:
            # Feedback Length vs Grade
            grading_df['FeedbackLength'] = grading_df['feedback'].str.len()
            fig7 = px.scatter(grading_df, x='grade', y='FeedbackLength',
                            trendline="lowess",
                            title="Grade vs Feedback Length Correlation",
                            labels={'FeedbackLength': 'Feedback Characters'})
            st.plotly_chart(fig7, use_container_width=True)

        with col2:
            # Word Cloud of Common Feedback
            text = ' '.join(grading_df['feedback'].dropna())
            wordcloud = WordCloud(width=800, height=400, 
                                 background_color='white').generate(text)
            plt.figure(figsize=(10,5))
            plt.imshow(wordcloud, interpolation='bilinear')
            plt.axis("off")
            plt.title("Most Common Feedback Terms")
            st.pyplot(plt.gcf(), use_container_width=True)

        # Grading Activity Timeline
        if 'timestamp' in grading_df.columns:
            grading_df['GradingDate'] = pd.to_datetime(grading_df['timestamp']).dt.date
            timeline = grading_df.groupby('GradingDate').size().reset_index(name='Count')
            fig8 = px.area(timeline, x='GradingDate', y='Count',
                          title="Daily Grading Activity Trend")
            st.plotly_chart(fig8, use_container_width=True)


    # =====================
    # Raw Data Section
    # =====================
    # st.header("📋 Raw Data Explorer")
    from database.operations import fetch_users, update_user_approvals_in_db
    st.header("📋 Raw Data Explorer")
    st.session_state.user_df = users_df

    # tab1, tab2, tab3 = st.tabs(["Users", "Sessions", "Grading"])
    tab1, tab3 = st.tabs(["Users", "Grading"])
    
    with tab1:
       users_df = fetch_users()
    
       edited_users = st.data_editor(
           users_df,
              column_config={
               "is_approved": st.column_config.CheckboxColumn(
                   "Approve User",
                   help="Toggle to approve/reject user access",
                   default=False
               )
           },
           disabled=["email", "role", "created_at"],
           use_container_width=True
       )
    
       if not users_df.equals(edited_users):
           if st.button("💾 Save Approvals", key="save_approvals"):
               try:
                   # Merge using consistent internal naming
                   changed = edited_users.merge(
                       users_df,
                       on='email',
                       suffixes=('_new', '_old')
                   )
                   changed = changed[changed['is_approved_new'] != changed['is_approved_old']]
                
                   if not changed.empty:
                       updates = changed[['email', 'is_approved_new']].rename(
                           columns={'is_approved_new': 'is_approved'}
                       )
                       update_user_approvals_in_db(updates)
                       st.cache_data.clear()
                       st.rerun()
                   else:
                       st.warning("⚠️ No changes detected")
                    
               except KeyError as e:
                   st.error(f"Column error: {str(e)}")
                   st.write("Current columns:", edited_users.columns.tolist())   
            
                   
    
    # with tab2:
    #     st.data_editor(sessions_df, use_container_width=True)

    with tab3:
        st.data_editor(grading_df, use_container_width=True)
   
   

    # =====================
    # Data Export Section
    # =====================
    st.header("📤 Data Export")
    
    if st.button("🖨️ Generate Comprehensive Report"):
        with st.spinner("Compiling report..."):
            report = generate_excel_report({
                'Users': users_df,
                'Sessions': sessions_df,
                'Grading': grading_df
            })
            st.download_button(
                label="📥 Download Full Report",
                data=report,
                file_name="comprehensive_analytics_report.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

if __name__ == "__main__":
    admin_dashboard()











# # pages/1_🧑‍💼_Admin_Dashboard.py
# import streamlit as st
# import pandas as pd
# from database.operations import get_all_users, approve_user, delete_user
# from database.connection import get_db_connection
# from utils.session import initialize_session, restrict_access, get_active_sessions
# from utils.security import get_all_grading_data, generate_excel_report

# def admin_dashboard():
#     initialize_session()
#     restrict_access(allowed_roles=['admin'])
#     st.title("Admin Dashboard🤵🏻")
#     st.write("Welcome, Admin! You can manage users and view all data.")
    
#     # User Management Section
#     st.subheader("User Management")
    
#     # Get users and convert to DataFrame
#     users = get_all_users()
#     df = pd.DataFrame(users, columns=["Email", "Role", "Approved"])
    
#     # Create editable grid with actions
#     col1, col2, col3 = st.columns([3, 2, 2])
    
#     with col1:
#         st.write("**User Email**")
#     with col2:
#         st.write("**Approval Status**")
#     with col3:
#         st.write("**Actions**")

#     for email, role, approved in users:
#         cols = st.columns([3, 2, 2])
        
#         with cols[0]:
#             st.write(email)
            
#         with cols[1]:
#             new_approval = st.checkbox(
#                 "Approved",
#                 value=approved,
#                 key=f"approve_{email}",
#                 on_change=handle_approval,
#                 args=(email, not approved)
#             )
#         with cols[2]:
#             if st.button("🗑️ Delete", key=f"delete_{email}"):
#                 handle_delete(email)

#     # Active Sessions Section
#     st.subheader("Active Sessions")
#     sessions = get_active_sessions()
#     if not sessions.empty:
#         st.dataframe(sessions)
#     else:
#         st.write("No active sessions found.")
    
#     # Grading Data Section
#     st.subheader("Grading Data")
#     grading_data = get_all_grading_data()
#     if not grading_data.empty:
#         st.dataframe(grading_data)
#     else:
#         st.write("No Grading found.")
    
#     # Export Section
#     if st.button("Export Analytics Data"):
#         analytics_excel = generate_excel_report(grading_data)
#         st.download_button(
#             "Download Analytics Report",
#             analytics_excel,
#             "analytics_report.xlsx"
#         )

# def handle_approval(email, approved):
#     """Handle approval status changes"""
#     conn = get_db_connection()
#     try:
#         with conn.cursor() as cursor:
#             cursor.execute(
#                 "UPDATE users SET is_approved = %s WHERE email = %s",
#                 (approved, email)
#             )
#             conn.commit()
#             st.success(f"User {email} approval status updated")
#     except Exception as e:
#         st.error(f"Error updating approval status: {str(e)}")
#     finally:
#         conn.close()
#     st.rerun()

# def handle_delete(email):
#     """Handle user deletion"""
#     conn = get_db_connection()
#     try:
#         with conn.cursor() as cursor:
#             cursor.execute(
#                 "DELETE FROM users WHERE email = %s",
#                 (email,)
#             )
#             conn.commit()
#             st.success(f"User {email} deleted successfully")
#     except Exception as e:
#         st.error(f"Error deleting user: {str(e)}")
#     finally:
#         conn.close()
#     st.rerun()

    
    

# if __name__ == "__main__":
#     admin_dashboard()






