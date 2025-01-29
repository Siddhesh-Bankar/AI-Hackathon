import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from tools.custom_tool import fetch_sales_data, generate_insights
from tools.nl2sqltask import getnl2sqlQuery
import re

st.set_page_config(page_title="Sales Data Insights", page_icon="📈", layout="wide")

# Custom CSS for styling
st.markdown(
    """
    <style>
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    .stApp {
        background-color: #f5f5f5;
    }
    .stDataFrame {
        border: 1px solid #ddd;
        border-radius: 5px;
    }
    .stMetric {
        background-color: white;
        padding: 10px;
        border-radius: 5px;
        box-shadow: 2px 2px 5px rgba(0, 0, 0, 0.1);
    }
    .stPlot {
        background-color: white;
        padding: 10px;
        border-radius: 5px;
        box-shadow: 2px 2px 5px rgba(0, 0, 0, 0.1);
        margin-bottom: 1rem;
    }
    .css-1adrpw5 {
        background-color: #f0f2f6;
        border: 1px solid #ddd;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("Sales Data Insights Dashboard")

st.write("Explore and analyze your sales data with interactive charts, key metrics, and insightful summaries.")

with st.sidebar:
    st.header("Analysis Options")
    # Take user input for the SQL query
    query_input = st.text_area("Enter SQL Query", "", height=150)

    if st.button("Fetch Data"):
        if query_input.strip():  # Ensure that the input is not empty
            # Pass the input query to getnl2sqlQuery function
            nl2sqlquery = getnl2sqlQuery(query_input)
            st.session_state.query = nl2sqlquery  # Store the result in session state

            try:
                # Now use the modified query (nl2sqlquery) to fetch the data
                sales_data = fetch_sales_data(nl2sqlquery)
                st.session_state.sales_data = sales_data
                st.success("Data fetched successfully!")
            except Exception as e:
                st.error(f"Error fetching data: {e}")
        else:
            st.error("Please enter a SQL query.")
            
if "sales_data" in st.session_state:
    sales_data = st.session_state.sales_data

    # 🛠 Ensure 'sales' column is numeric
    if 'sales' in sales_data.columns:
        sales_data['sales'] = pd.to_numeric(sales_data['sales'], errors='coerce')

    if not sales_data.empty:
        st.subheader("Sales Data")
        st.data_editor(sales_data, num_rows="dynamic")

        # 🛠 Display Key Metrics
        if 'sales' in sales_data.columns:
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Sales", f"${sales_data['sales'].sum():,.2f}")
            with col2:
                st.metric("Average Sales", f"${sales_data['sales'].mean():,.2f}")
            with col3:
                st.metric("Number of Transactions", len(sales_data))

        # 📊 Sales Analysis
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
            insights = generate_insights(sales_data)
            st.subheader("Generated Insights")
            st.write(insights)

else:
    st.info("Enter a SQL query to fetch data.")
