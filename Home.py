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


# THIS MUST BE THE VERY FIRST STREAMLIT COMMAND
st.set_page_config(
    page_title="Atech SmartAssess",
    page_icon="📝",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get help': None,
        'Report a bug': None,
        'About': None
    }
)

# Then add this CSS override IMMEDIATELY AFTER
st.markdown("""
    <style>
    /* Remove Snowflake branding */
    .stApp footer:first-child { display: none !important; }
    
    /* Hide About dialog remnants */
    div[data-modal-container='true'] > div:has(> div > div > div > div[aria-label="About"]),
    iframe[title="About"] {
        display: none !important;
    }
    </style>
""", unsafe_allow_html=True)






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




st.markdown("""
    <style>
    @keyframes float {
        0% { transform: translateY(-50%); }
        50% { transform: translateY(-50%) translateX(-10px); }
        100% { transform: translateY(-50%); }
    }

    .menu-indicator-container {
        position: fixed;
        top: 10%;
        right: 60px;
        z-index: 1000;
        pointer-events: none;
        display: flex;
        align-items: center;
        gap: 10px;
        transition: opacity 0.5s ease;
    }

    .menu-indicator-arrow {
        width: 15px;
        height: 15px;
        border-top: 4px solid #FF474C;
        border-right: 4px solid #FF474C;
        transform: rotate(45deg);
        animation: float 2s infinite;
    }

    .menu-indicator-text {
        color: #FFFDD0 !important;
        background: #581845;
        padding: 8px 11px;
        border-radius: 5px;
        font-size: 11px;
        white-space: nowrap;
        box-shadow: 0 2px 5px rgba(0,0,0,0.2);
        transition: inherit;
    }

    .hidden-indicator {
        opacity: 0 !important;
    }
    </style>

    <div class="menu-indicator-container" id="scroll-sensitive-indicator">
        <div class="menu-indicator-text">Click 3 dots for Menu Options (Rerun or Refresh page & Switch to dark mode)! ▶</div>
        <div class="menu-indicator-arrow"></div>
    </div>

    <script>
    // Hide on scroll
    let lastScroll = 0;
    const indicator = document.getElementById('scroll-sensitive-indicator');
    
    window.addEventListener('scroll', () => {
        indicator.classList.add('hidden-indicator');
        lastScroll = window.pageYOffset;
    });

    // Show only on fresh load
    window.addEventListener('load', () => {
        if(performance.navigation.type === 0) { // Type 0 is fresh load
            indicator.classList.remove('hidden-indicator');
        }
    });
    </script>
""", unsafe_allow_html=True)

# Add this to force fresh state on rerun
if 'first_load' not in st.session_state:
    st.session_state.first_load = True
    st.rerun()



# Main header
# Initialize session state
initialize_session()


from database.operations import get_admin_metrics
import random
# Replace the main header section with this conditional code
if st.session_state.logged_in:  
    pass 





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

        #This is for playlists - src="https://www.youtube.com/embed/videoseries?list=PLiSQn44JDXvTVF-Q9mCH_goesRpxvGxmV&autoplay=1&mute=1&loop=1"      
    else:    
        # Video section
        
        # Video section with responsive styling
        st.markdown("""
            <div style="position: relative; padding-bottom: 56.25%; height: 0; overflow: hidden; border-radius: 15px; margin: 20px 0;">
                <iframe src="https://www.youtube.com/embed/Q_DG6CZnIDE?autoplay=1&mute=1" 
                        style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; border: 0;" 
                        allow="accelerometer; autoplay; encrypted-media; gyroscope; picture-in-picture" 
                        allowfullscreen></iframe>
            </div>
        """, unsafe_allow_html=True)
          
        # # st.write("This video demonstrates how students can retrieve their assignments from Canvas LMS and evaluate them using the ATech SmartAssess app.")
        st.markdown("""<p style="color: white;">
                    AMSTERDAM TECH - A SKILLS-BASED INSTITUTION BUILT FOR THE DIGITAL ECONOMY
                  </p>""", unsafe_allow_html=True)
        st.markdown("<br><br>", unsafe_allow_html=True)  # Adds two line breaks for spacing




        # import streamlit as st
        import datetime

        # Create two columns
        col1, col2 = st.columns([3, 2])  # Adjust ratio as needed

        # Get current date
        today = datetime.date.today()
        day_index = today.day % 7  # Ensures selection changes daily

        # Dictionary of Complex Code Snippets with Explanations
        code_snippets = {
            0: ("python", """# Fibonacci sequence using recursion
        def fibonacci(n):
            if n <= 0:
                return "Invalid Input"
            elif n == 1:
                return 0
            elif n == 2:
                return 1
            else:
                return fibonacci(n-1) + fibonacci(n-2)

        print(fibonacci(10))  # Output: 34
        """, 
            """### 
            🔍 Explanation: Fibonacci in Python
            - This function **recursively** calculates Fibonacci numbers.
            - Base cases: `fibonacci(1) = 0`, `fibonacci(2) = 1`.
            - For `n > 2`, it returns `fibonacci(n-1) + fibonacci(n-2)`.
            - Example: `fibonacci(10) = 34`.
            - ❗ **Tip:** Recursion is not efficient for large numbers. Consider **memoization**."""),

            1: ("javascript", """// Fetch API example in JavaScript
        async function fetchData() {
            try {
                let response = await fetch('https://api.example.com/data');
                let data = await response.json();
                console.log(data);
            } catch (error) {
                console.error('Error fetching data:', error);
            }
        }
        fetchData();
        """, 
            """### 
            🔍 Explanation: Fetch API in JavaScript
            - This code makes an **asynchronous HTTP request** using `fetch()`.
            - `await` waits for the response to arrive.
            - `.json()` converts the response to a **JavaScript object**.
            - **Error Handling:** If an error occurs, it’s caught in the `catch` block."""),

            2: ("c", """// Reverse a string in C
        #include <stdio.h>
        #include <string.h>

        void reverseString(char *str) {
            int length = strlen(str);
            for (int i = 0; i < length / 2; i++) {
                char temp = str[i];
                str[i] = str[length - i - 1];
                str[length - i - 1] = temp;
            }
        }

        int main() {
            char str[] = "Hello, World!";
            reverseString(str);
            printf("Reversed: %s\\n", str);
            return 0;
        }
        """, 
            """### 
            🔍 Explanation: String Reversal in C
            - Uses **pointers & character swapping** to reverse a string.
            - Swaps `str[i]` with `str[length - i - 1]` iteratively.
            - **Efficient** because it modifies the string **in-place**.
            - Uses `strlen()` from `<string.h>` to find length."""),

            3: ("java", """// Bubble Sort in Java
        public class BubbleSort {
            public static void main(String[] args) {
                int[] arr = {5, 3, 8, 1, 2};
                bubbleSort(arr);
                for (int num : arr) {
                    System.out.print(num + " ");
                }
            }

            public static void bubbleSort(int[] arr) {
                int n = arr.length;
                for (int i = 0; i < n - 1; i++) {
                    for (int j = 0; j < n - i - 1; j++) {
                        if (arr[j] > arr[j + 1]) {
                            int temp = arr[j];
                            arr[j] = arr[j + 1];
                            arr[j + 1] = temp;
                        }
                    }
                }
            }
        }
        """, 
            """### 
            🔍 Explanation: Bubble Sort in Java
            - Bubble Sort is a **comparison-based sorting algorithm**.
            - Iterates through the array, **swapping adjacent elements** if needed.
            - **Worst-case complexity:** O(n²) (slow for large datasets).
            - **Alternative:** Use **Merge Sort** or **Quick Sort** for better efficiency."""),

            4: ("sql", """-- SQL Query: Get Top 5 Customers by Purchase Amount
        SELECT customer_id, SUM(purchase_amount) AS total_spent
        FROM purchases
        GROUP BY customer_id
        ORDER BY total_spent DESC
        LIMIT 5;
        """, 
            """### 
            🔍 Explanation: SQL Query for Top Customers
            - Uses `SUM(purchase_amount)` to get the total spent per customer.
            - `GROUP BY customer_id` groups purchases by customer.
            - `ORDER BY total_spent DESC` sorts from **highest spender to lowest**.
            - `LIMIT 5` returns **only the top 5 customers**."""),

            5: ("html", """<!-- Responsive Navbar in HTML & CSS -->
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Navbar</title>
            <style>
                nav { background: #333; padding: 10px; }
                nav a { color: white; padding: 10px; text-decoration: none; }
                @media (max-width: 600px) {
                    nav { text-align: center; }
                }
            </style>
        </head>
        <body>
            <nav>
                <a href="#">Home</a>
                <a href="#">About</a>
                <a href="#">Contact</a>
            </nav>
        </body>
        </html>
        """, 
            """### 
            🔍 Explanation: Responsive Navbar (HTML & CSS)
            - Uses a `<nav>` element for navigation.
            - CSS styles the navbar with a **dark background**.
            - `@media (max-width: 600px)` centers the navbar for mobile screens."""),

            6: ("bash", """#!/bin/bash
        # Backup Script: Backs up a directory

        SOURCE_DIR="/home/user/Documents"
        BACKUP_DIR="/home/user/Backups"

        mkdir -p $BACKUP_DIR
        tar -czf $BACKUP_DIR/backup_$(date +%Y-%m-%d).tar.gz $SOURCE_DIR
        echo "Backup completed!"
        """, 
            """### 
            🔍 Explanation: Backup Script in Bash
            - **Creates a compressed backup** of `SOURCE_DIR` using `tar`.
            - `mkdir -p $BACKUP_DIR` ensures the backup folder exists.
            - Backup is saved as `backup_YYYY-MM-DD.tar.gz`.
            - 🛡 **Use case:** Automate daily system backups."""),

        }

        # Get today's code and explanation
        language, code_of_the_day, explanation = code_snippets[day_index]

        # Display Code in Column 1
        with col1:
            # st.header("📌 Code of the Day")
            st.markdown("<h1 style='color: gray;'>📌 Code of the Day</h1>", unsafe_allow_html=True)
            st.code(code_of_the_day, language=language)  # Dynamically highlights syntax

        # Display Explanation in Column 2
        with col2:
            st.markdown("<br><br><br>", unsafe_allow_html=True)  # Adds two line breaks for spacing
            # st.subheader("📖 Explanation")
            st.markdown(explanation)  # Displays formatted explanation

                
else:
    page = st.sidebar.radio("Navigation", ["Login", "Register"])
    if page == "Login":
        login_page()
    else:
        registration_page()    

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





