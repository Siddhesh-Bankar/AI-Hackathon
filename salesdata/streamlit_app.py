import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from tools.custom_tool import fetch_sales_data, generate_insights 
from tools.nl2sqltask import getnl2sqlQuery
from tools.insighttask import getInsights
from tools.generatechart import getCharts
from tools.csvrag import getCSVInsights
import time

# Set page config FIRST
st.set_page_config(page_title="Sales Data Insights", page_icon="📈", layout="wide")

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
    
    </style>
    """,
    unsafe_allow_html=True,
)

def stream_result(formatted_output):
    output_parts = formatted_output.split("\n")
    
    for part in output_parts:
        yield part + "\n"
        time.sleep(0.5)  # Simulate a delay between each chunk to mimic streaming

# Title and description
st.title("Sales Data Insights Chat")
st.write("Chat with the app to explore and analyze your sales data with interactive charts, key metrics, and insightful summaries.")


# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Accept user input
if prompt := st.chat_input("Enter your query or command"):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)

    # Process the user input
    if prompt.strip():  # Ensure that the input is not empty
        try:
            # Pass the input query to getnl2sqlQuery function
            nl2sqlquery = getnl2sqlQuery(prompt)
            st.session_state.query = nl2sqlquery  # Store the result in session state

            # Now use the modified query (nl2sqlquery) to fetch the data
            sales_data = fetch_sales_data(nl2sqlquery)
            st.session_state.sales_data = sales_data
            response = "Data fetched successfully!"
        except Exception as e:
            response = f"Error fetching data: {e}"
    else:
        response = "Please enter a SQL query."

    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        st.markdown(response)
    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": response})

# Display sales data and insights if available
if "sales_data" in st.session_state:
    sales_data = st.session_state.sales_data

    # Ensure 'sales' column is numeric
    if 'sales' in sales_data.columns:
        sales_data['sales'] = pd.to_numeric(sales_data['sales'], errors='coerce')

    if not sales_data.empty:
        st.subheader("Sales Data")
        st.data_editor(sales_data, num_rows="dynamic")

        # Display Key Metrics
        if 'sales' in sales_data.columns:
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Sales", f"${sales_data['sales'].sum():,.2f}")
            with col2:
                st.metric("Average Sales", f"${sales_data['sales'].mean():,.2f}")
            with col3:
                st.metric("Number of Transactions", len(sales_data))

        # Sales Analysis
        st.subheader("Sales Analysis")

        if 'region' in sales_data.columns and 'sales' in sales_data.columns:
            fig1, ax1 = plt.subplots(figsize=(8, 4))
            sns.barplot(x='region', y='sales', data=sales_data, ax=ax1, hue='region', palette="viridis")
            ax1.set_title('Sales by Region', fontsize=10)
            ax1.set_xlabel('Region', fontsize=12)
            ax1.set_ylabel('Sales', fontsize=12)
            plt.xticks(rotation=45, ha='right')
            st.pyplot(fig1)

        if 'date' in sales_data.columns and 'sales' in sales_data.columns:
            sales_data['date'] = pd.to_datetime(sales_data['date'])
            sales_data = sales_data.sort_values(by='date')
            fig2, ax2 = plt.subplots(figsize=(8, 4))
            sns.lineplot(x='date', y='sales', data=sales_data, ax=ax2)
            ax2.set_title('Sales Over Time', fontsize=10)
            ax2.set_xlabel('Date', fontsize=12)
            ax2.set_ylabel('Sales', fontsize=12)
            st.pyplot(fig2)
    else:
        st.warning("No data returned for the given query.")

    if st.button("Generate Insights"):
        with st.spinner("Generating insights..."):
            # insights = generate_insights(sales_data)
            insightsfromcrew=getInsights(sales_data)
            # chartsfromcrew=getCharts(sales_data)
            
            # st.subheader("Generated Insights")
            # st.write(insights)
            # st.subheader("Generated Insights from crew ai")
            # st.write(insightsfromcrew)
            # st.write(chartsfromcrew)
            csvinsights=getCSVInsights()
            for chunk in stream_result(csvinsights):
                st.write(chunk) 
            
            print(csvinsights)

else:
    st.info("Enter a query to fetch data.")