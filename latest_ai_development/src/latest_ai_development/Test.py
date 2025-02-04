import streamlit as st
import streamlit.components.v1 as components

# Set page config first
st.set_page_config(page_title="Sales Insights Login", page_icon="🔒", layout="centered")

# Custom CSS for the login page
def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# Load custom CSS
local_css("styles.css")

# Login Page
def login_page():
    st.markdown(
        """
        <div class="login-container">
            <h2>Sales Insights Login</h2>
            <form class="login-form">
                <label for="username">Username</label>
                <input type="text" id="username" name="username" placeholder="Enter your username" required>
                
                <label for="password">Password</label>
                <input type="password" id="password" name="password" placeholder="Enter your password" required>
                
                <button type="submit">Login</button>
            </form>
        </div>
        """,
        unsafe_allow_html=True
    )

# Main function to run the app
def main():
    login_page()

if __name__ == "__main__":
    main()