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

SCOPES = ['https://www.googleapis.com/auth/gmail.send']

def stream_result(formatted_output):
    """Yields output in a streaming format."""
    for part in formatted_output.split("\n"):
        yield part + "\n"
        time.sleep(0.5)

def login():
    """Handles user authentication."""
    st.title("Login to Sales Data Insights! 🔑")
    with st.form(key="login_form"):
        username = st.text_input("Username 👤")
        password = st.text_input("Password 🔒", type="password")
        login_button = st.form_submit_button("Login ➡️")
    
    if login_button:
        if authenticate_user(username, password):
            st.session_state.update({"logged_in": True, "username": username, "login_successful": True})
            st.success(f"Welcome, {username}! 🎉")
            st.rerun()
        else:
            st.session_state["login_successful"] = False
            st.error("Invalid username or password ❌")

def set_page_config():
    """Sets page configuration."""
    st.set_page_config(page_title="Virtual Sales Agent Chat", layout="wide", initial_sidebar_state="expanded")

def set_page_style():
    """Applies custom styles."""
    st.markdown(f"""
        <style>
        {open("assets/style.css").read()}
        </style>
    """, unsafe_allow_html=True)

def setup_sidebar():
    """Configures the sidebar UI."""
    if not st.session_state.get("logged_in"):
        return
    
    with st.sidebar:
        st.markdown("""
            <div class="agent-profile">
                <div class="profile-header">
                    <div class="avatar">🤖</div>
                    <h1>Sales Agent</h1>
                </div>
                <div class="feature-list">
                    <div class="feature-item"><span class="icon">🛒</span> <span>Browse File</span></div>
                    <div class="feature-item"><span class="icon">🎯</span> <span>Get personalized recommendations</span></div>
                </div>
                <div class="status-card"><div class="status-indicator"></div> <span>Ready to Assist</span></div>
            </div>
        """, unsafe_allow_html=True)
        
        if st.button("File Upload 📂"):
            st.session_state["show_file_upload"] = True
        
        st.markdown("---")
        if st.button("🔄 Start New Chat"):
            st.session_state.clear()
            st.rerun()
        
        if st.button("🔍 Visualize Workflow"):
            st.image("assets/graph.png")

def handle_file_upload():
    """Handles CSV file uploads."""
    uploaded_file = st.file_uploader("Choose a CSV file 📂", type="csv")
    if uploaded_file:
        csv_data = pd.read_csv(uploaded_file)
        st.subheader("Uploaded CSV Data 📊")
        st.dataframe(csv_data)
        if st.button("Insert into Database 🗃️"):
            result_message = insert_data_into_database(csv_data, "sales_data")
            st.success(result_message + " ✅") if "Successfully inserted" in result_message else st.error(result_message + " ❌")

def chat_interface():
    """Manages chat-based interactions."""
    if "messages" not in st.session_state:
        st.session_state["messages"] = []
    
    for message in st.session_state["messages"]:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    prompt = st.chat_input("Enter your query or command")
    if prompt:
        st.session_state["messages"].append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        try:
            nl2sqlquery = getnl2sqlQuery(prompt)
            sales_data = fetch_sales_data(nl2sqlquery)
            st.session_state.update({"query": nl2sqlquery, "sales_data": sales_data})
            response = "Data fetched successfully!"
        except Exception as e:
            response = f"Error fetching data: {e}"
        
        with st.chat_message("assistant"):
            st.markdown(response)
        st.session_state["messages"].append({"role": "assistant", "content": response})

def display_sales_data():
    """Displays sales data with insights."""
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

def main():
    """Main function to execute the app."""
    set_page_config()
    set_page_style()
    
    if not st.session_state.get("logged_in"):
        login()
        return
    
    setup_sidebar()
    if st.session_state.get("show_file_upload"):
        handle_file_upload()
    chat_interface()
    display_sales_data()

if __name__ == "__main__":
    main()