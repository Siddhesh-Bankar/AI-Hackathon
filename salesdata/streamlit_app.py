import json
import uuid
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import time
from google.auth.transport.requests import Request 
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.messages.tool import ToolMessage
from tools.custom_tool import fetch_sales_data, generate_insights, insert_data_into_database, authenticate_user
from tools.nl2sqltask import getnl2sqlQuery
from tools.insighttask import getInsights
from tools.demand import getDemandJson
 
SCOPES = ['https://www.googleapis.com/auth/gmail.send']
 
def stream_result(formatted_output):
    for part in formatted_output.split("\n"):
        yield part + "\n"
        time.sleep(0.5)
 
def login():
    st.title("Login to Sales Data Insights! 🔑")
    with st.form(key="login_form"):
        username = st.text_input("Username 👤")
        password = st.text_input("Password 🔒", type="password")
        login_button = st.form_submit_button("Login ➡️")
   
    if login_button:
        if authenticate_user(username, password):
            st.session_state.update({
                "logged_in": True,
                "username": username,
                "login_successful": True,
                "show_file_upload": False,
                "show_chat": True  # Ensure Sales Chat is shown after login
            })
            st.success(f"Welcome, {username}! 🎉")
            st.rerun()
        else:
            st.session_state["login_successful"] = False
            st.error("Invalid username or password ❌")
 
def logout():
    """Clears session state and redirects to the login page."""
    st.session_state.clear()
    st.session_state["logged_in"] = False
    st.success("Logged out successfully! Redirecting to login... 🔄")
    time.sleep(1)
    st.rerun()
 
def set_page_config():
    st.set_page_config(page_title="Sales Agent", layout="wide", initial_sidebar_state="expanded")
 
def set_page_style():
    st.markdown(f"""
        <style>
        {open("assets/style.css").read()}
        </style>
    """, unsafe_allow_html=True)
 
def setup_sidebar():
    if not st.session_state.get("logged_in"):
        return
   
    with st.sidebar:
        st.markdown("""<div class="agent-profile">
            <div class="profile-header">
                <div class="avatar">🤖</div>
                <h1>Sales Agent</h1>
            </div>
            <div class="feature-list">
                <div class="feature-item"><span class="icon">🛒</span> <span>Browse File</span></div>
                <div class="feature-item"><span class="icon">🎯</span> <span>Get personalized recommendations</span></div>
            </div>
            <div class="status-card"><div class="status-indicator"></div> <span>Ready to Assist</span></div>
        </div>""", unsafe_allow_html=True)
 
        # ✅ Apply CSS Class to Buttons
       
        if st.button("📂 File Upload", use_container_width=True, key="file_upload_btn"):
            st.session_state["show_file_upload"] = True
            st.session_state["show_chat"] = False  # Hide Chat
            st.session_state["demand_chat"] = False
 
        if st.button("💬 Sales Chat", use_container_width=True, key="sales_chat_btn"):
            st.session_state["demand_chat"] = False
            st.session_state["show_chat"] = True
            st.session_state["show_file_upload"] = False  # Hide File Upload

        if st.button("💬Demand", use_container_width=True, key="demand_chat_btn"):
            st.session_state["demand_chat"] = True
            st.session_state["show_file_upload"] = False 
            st.session_state["show_chat"] = False
       
        st.markdown("---")
 
        if st.button("🔄 Start New Chat", use_container_width=True):
            keys_to_keep = {"logged_in", "username", "login_successful", "show_file_upload", "show_chat"}
            st.session_state = {key: st.session_state[key] for key in keys_to_keep if key in st.session_state}
            st.session_state["messages"] = []  # Clear chat history
            st.rerun()
       
 
        st.markdown("---")
 
        # 🔴 Logout Button
        if st.button("🚪 Logout", use_container_width=True):
            logout()
 
def handle_file_upload():
    st.subheader("📂 File Upload")
    uploaded_file = st.file_uploader("Choose a CSV file 📂", type="csv")
    if uploaded_file:
        csv_data = pd.read_csv(uploaded_file)
        st.subheader("Uploaded CSV Data 📊")
        st.dataframe(csv_data)
        if st.button("Insert into Database 🗃️"):
            result_message = insert_data_into_database(csv_data, "sales_data")
            st.success(result_message + " ✅") if "Successfully inserted" in result_message else st.error(result_message + " ❌")

def is_valid_query(query):
    query = query.strip().lower()
    return "select" in query

def demand(Json):
    st.title("📦 Product Ordering System")
    
    # Initialize session state for orders if not already present
    if 'orders' not in st.session_state:
        st.session_state.orders = {}

    # Loop through products and create boxes
    for idx, product in enumerate(Json):
        with st.container():
            st.markdown("---")  # Add a horizontal separator
            col1, col2, col3, col4 = st.columns([3, 2, 3, 2])

            with col1:
                st.subheader(f"🛒 {product['product_name']}")

            with col2:
                st.write(f"**Quantity:** {product['quantity']}")

            with col3:
                st.write(f"**Manufacturer:** {product['manufacturer']}")

            with col4:
                order_key = f"order_{idx}"
                if order_key not in st.session_state.orders:
                    st.session_state.orders[order_key] = False

                if st.button(f"Order {idx+1}", key=order_key):
                    st.session_state.orders[order_key] = True

                if st.session_state.orders[order_key]:
                    st.success(f"✅ Order placed for {product['product_name']}!")

    st.markdown("---")

def person():
    st.title("👤 Person Information")
    st.write("This is the person section. You can add functionality related to person data here.")

def chat_interface():
    if not st.session_state.get("show_chat"):
        return
   
    st.subheader("💬 Sales Chat")
    st.write("Chat with the app to explore and analyze your sales data!")
 
    if "messages" not in st.session_state:
        st.session_state["messages"] = []
   
    for message in st.session_state["messages"]:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
   
    if prompt := st.chat_input("Enter your query or command"):
        st.session_state["messages"].append({"role": "user", "content": prompt})
        st.session_state.sales_data=None
        with st.chat_message("user"):
            st.markdown(prompt)
 
        if prompt.strip():
            try:
                nl2sqlquery = getnl2sqlQuery(prompt)
                st.session_state.query = nl2sqlquery
                if is_valid_query(nl2sqlquery):
                    sales_data = fetch_sales_data(nl2sqlquery)
                    st.session_state.sales_data = sales_data
                else:
                    st.markdown(nl2sqlquery)
                
                response = "Data fetched successfully!"
            except Exception as e:
                response = f"Error fetching data: {e} ❌"
        else:
            response = "Please enter a valid query."
 
        with st.chat_message("assistant"):
            st.markdown(response)
        st.session_state["messages"].append({"role": "assistant", "content": response})
 
def display_sales_data():
    sales_data = st.session_state.get("sales_data")
    if sales_data is not None and not sales_data.empty:
        st.subheader("Sales Data 📊")
        st.data_editor(sales_data, num_rows="dynamic")
       
        st.subheader("Key Metrics")
        if 'sales' in sales_data.columns:
            col1, col2, col3 = st.columns(3)
            col1.metric("Total Sales 💰", f"${sales_data['sales'].sum():,.2f}")
            col2.metric("Average Sales 💵", f"${sales_data['sales'].mean():,.2f}")
            col3.metric("Number of Transactions 🧮", len(sales_data))
       
        if 'region' in sales_data.columns and 'sales' in sales_data.columns:
            st.subheader("Sales Analysis")
            fig, ax = plt.subplots(figsize=(8, 6))
            sns.barplot(x='region', y='sales', data=sales_data, ax=ax, palette="viridis")
            ax.set_title('Sales by Region 📊', fontsize=16)
            ax.set_xlabel('Region 🌍', fontsize=12)
            ax.set_ylabel('Sales 💸', fontsize=12)
            plt.xticks(rotation=45, ha='right')
            st.pyplot(fig)
       
        if st.button("Generate Insights"):
            with st.spinner("Generating insights..."):
                st.subheader("Generated Insights from AI")
                st.write(getInsights(sales_data))
def demand():
        prompt="Give me the top 5 product list with has highest sales,its manufacturer and its quantity present in the product_data"
        st.markdown('<div class="compact-buttons">', unsafe_allow_html=True)
        if st.button("Order"):
            # Fetch and process demand data if not already in session state
            if 'demand_data' not in st.session_state:
                with st.spinner("Fetching demand data..."):
                    nl2sqlquery = getnl2sqlQuery(prompt)
                    nl2sqlquery = nl2sqlquery.replace("sql", "").strip()
                    st.session_state.demand_data = fetch_sales_data(nl2sqlquery)
                    st.session_state.demandJson = getDemandJson(st.session_state.demand_data)
            # Display the demand data
                demand(st.session_state.demandJson)
        if st.button("Person"):
            # Call the person function
            person()
        st.markdown('</div>', unsafe_allow_html=True)


def main():
    set_page_config()
    set_page_style()
   
    if not st.session_state.get("logged_in"):
        login()
        return
   
    setup_sidebar()
   
    # Show only the selected section
    if st.session_state.get("show_file_upload"):
        handle_file_upload()
    elif st.session_state.get("show_chat"):
        chat_interface()
    elif st.session_state.get("demand_chat"):
        demand()
            
    display_sales_data()
 
if __name__ == "__main__":
    main()
 