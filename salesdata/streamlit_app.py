
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from tools.custom_tool import fetch_sales_data, generate_insights, insert_data_into_database, authenticate_user
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
import os
import base64
import time
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from tools.nl2sqltask import getnl2sqlQuery
from tools.insighttask import getInsights
from google.auth.transport.requests import Request
from pathlib import Path
from tools.demand import getDemandJson
# from tools.csvrag import getCSVInsights
import time
import json



st.set_page_config(page_title="Sales Data Insights", page_icon="📈", layout="centered")

# Custom CSS for styling
st.markdown(
    """
    <style>
    .main {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        max-width: 800px;
        margin: auto;
    }
    .compact-buttons {
        display: flex;
        gap: 10px;
        margin-bottom: 20px;
    }
    .compact-buttons button {
        flex: 1;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

SCOPES = ['https://www.googleapis.com/auth/gmail.send']

def stream_result(formatted_output):
    output_parts = formatted_output.split("\n")
    
    for part in output_parts:
        yield part + "\n"
        time.sleep(0.5)  

def login():
    st.title("Login to Sales Data Insights! 🔑")

    with st.form(key="login_form"):
        username = st.text_input("Username 👤")
        password = st.text_input("Password 🔒", type="password")
        
        login_button = st.form_submit_button("Login ➡️")  

    if login_button:
        with st.spinner("Logging in..."):
            user_details = authenticate_user(username, password)
        
            if user_details:
                st.session_state.logged_in = True
                st.session_state.username = user_details['username']
                st.session_state.login_successful = True
                st.success(f"Welcome, {username}! 🎉")
                st.session_state.dashboard_redirect = True  
                st.rerun()  
            else:
                st.session_state.login_successful = False
                st.error("Invalid username or password ❌") 

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

def is_valid_query(query):
    # Normalize the query to lowercase and remove leading/trailing spaces
    query = query.strip().lower()
    # Check if the query contains 'select' (not necessarily at the beginning)
    return "select" in query

def person():
    st.title("👤 Person Information")
    st.write("This is the person section. You can add functionality related to person data here.")
# Main Dashboard Page (Only visible after login)
def dashboard():
    st.title("Sales Data Insights Chat")
    st.write("Chat with the app to explore and analyze your sales data with interactive charts, key metrics, and insightful summaries.")
    
    with st.sidebar:
        if st.button("Back to Login 🔙"):
            st.session_state.logged_in = False
            st.session_state.dashboard_redirect = False
            st.session_state.username = None
            st.session_state.login_successful = False
            st.session_state.sales_data = None  
            st.session_state.query = None  
            st.rerun()  

        st.subheader("Upload CSV to Insert into Database 📥")
        uploaded_file = st.file_uploader("Choose a CSV file 📂", type="csv")

        if uploaded_file:
            csv_data = pd.read_csv(uploaded_file)
            st.subheader("Uploaded CSV Data 📊")
            st.dataframe(csv_data)

            if st.button("Insert into Database 🗃️"):
                table_name = "sales_data"
                result_message = insert_data_into_database(csv_data, table_name)
                if "Successfully inserted" in result_message:
                    st.success(result_message + " ✅")
                else:
                    st.error(result_message + " ❌")

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("Enter your query or command"):
        st.session_state.messages.append({"role": "user", "content": prompt})
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
                    print("Invalid query. Query execution aborted.")
                    st.markdown(nl2sqlquery)
                
                response = "Data fetched successfully!"
            except Exception as e:
                response = f"Error fetching data: {e}"
        else:
            response = "Please enter a SQL query."

        with st.chat_message("assistant"):
            st.markdown(response)
        st.session_state.messages.append({"role": "assistant", "content": response})

    if "sales_data" in st.session_state and st.session_state.sales_data is not None:
        sales_data = st.session_state.sales_data
        if not sales_data.empty:
            st.subheader("Sales Data 📊")
            st.data_editor(sales_data, num_rows="dynamic")

            st.subheader("Key Metrics")
            if 'sales' in sales_data.columns:
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Total Sales 💰", f"${sales_data['sales'].sum():,.2f}")
                with col2:
                    st.metric("Average Sales 💵", f"${sales_data['sales'].mean():,.2f}")
                with col3:
                    st.metric("Number of Transactions 🧮", len(sales_data))

                total_sales = f"${sales_data['sales'].sum():,.2f} 💰"
                average_sales = f"${sales_data['sales'].mean():,.2f} 💵"
                num_transactions = len(sales_data)

                st.subheader("Sales Analysis")

                region_chart_path = ""
                time_chart_path = ""

                if 'region' in sales_data.columns and 'sales' in sales_data.columns:
                    fig1, ax1 = plt.subplots(figsize=(8, 6))
                    sns.barplot(x='region', y='sales', data=sales_data, ax=ax1, palette="viridis")
                    ax1.set_title('Sales by Region 📊', fontsize=16)
                    ax1.set_xlabel('Region 🌍', fontsize=12)
                    ax1.set_ylabel('Sales 💸', fontsize=12)
                    plt.xticks(rotation=45, ha='right')
                    st.pyplot(fig1)

                    region_chart_path = "sales_by_region.png"
                    fig1.savefig(region_chart_path, format="png")

                if 'date' in sales_data.columns and 'sales' in sales_data.columns:
                    sales_data['date'] = pd.to_datetime(sales_data['date'])
                    sales_data = sales_data.sort_values(by='date')
                    fig2, ax2 = plt.subplots(figsize=(8, 6))
                    sns.lineplot(x='date', y='sales', data=sales_data, ax=ax2, palette="magma")
                    ax2.set_title('Sales Over Time 📆', fontsize=16)
                    ax2.set_xlabel('Date 📅', fontsize=12)
                    ax2.set_ylabel('Sales 💵', fontsize=12)
                    st.pyplot(fig2)

                    time_chart_path = "sales_over_time.png"
                    fig2.savefig(time_chart_path, format="png")


        if st.button("Generate Insights"):
            with st.spinner("Generating insights..."):
                insightsfromcrew = getInsights(sales_data)
                st.subheader("Generated Insights from crew ai")
                st.write(insightsfromcrew)
                

if "logged_in" not in st.session_state or not st.session_state.logged_in:
    login()

elif st.session_state.get("dashboard_redirect", False):
        prompt="Give me the top 5 product list with has highest sales,its manufacturer and its quantity present in the product_data"
        page = st.sidebar.radio("Go to", ["Sales Chat", "Demand"])
        if page == "Sales Chat":
            dashboard()
        elif page == "Demand":
            # Add two buttons for "Order" and "Person" in a compact layout
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

    
else:
    st.warning("Please log in to access the dashboard ⚠️.")

