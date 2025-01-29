import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from tools.custom_tool import fetch_sales_data, generate_insights
from tools.nl2sqltask import getnl2sqlQuery

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
        background-color: #f5f5f5; /* Light gray background */
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
    .css-1adrpw5{
        background-color: #f0f2f6;
        border: 1px solid #ddd;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("Sales Data Insights Dashboard")

st.write("""
Explore and analyze your sales data with interactive charts, key metrics, and insightful summaries.
""")

with st.sidebar:
    st.header("Analysis Options")
    nl2sqlquery=getnl2sqlQuery()
    print(nl2sqlquery)
    query_input = st.text_area("Enter SQL Query", nl2sqlquery, height=150)
    if st.button("Fetch Data"):
        st.session_state.query = query_input
        try:
            sales_data = fetch_sales_data(st.session_state.query)
            st.session_state.sales_data = sales_data
            st.success("Data fetched successfully!")
        except Exception as e:
            st.error(f"Error fetching data: {e}")

if "sales_data" in st.session_state:
    sales_data = st.session_state.sales_data
    if not sales_data.empty:
        st.subheader("Sales Data")
        st.data_editor(sales_data, num_rows="dynamic")

        st.subheader("Key Metrics")
        if 'sales' in sales_data.columns:
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Sales", f"${sales_data['sales'].sum():,.2f}")  # Add comma formatting
            with col2:
                st.metric("Average Sales", f"${sales_data['sales'].mean():,.2f}")
            with col3:
                st.metric("Number of Transactions", len(sales_data))

            st.subheader("Sales Analysis")

            if 'region' in sales_data.columns and 'sales' in sales_data.columns:
                fig1, ax1 = plt.subplots(figsize=(8, 6))  # Adjust figure size for better visuals
                sns.barplot(x='region', y='sales', data=sales_data, ax=ax1, palette="viridis") # Use a better color palette
                ax1.set_title('Sales by Region', fontsize=16)
                ax1.set_xlabel('Region', fontsize=12)
                ax1.set_ylabel('Sales', fontsize=12)
                plt.xticks(rotation=45, ha='right')  # Rotate x-axis labels if needed
                st.pyplot(fig1)

            if 'date' in sales_data.columns and 'sales' in sales_data.columns:
                sales_data['date'] = pd.to_datetime(sales_data['date'])
                sales_data = sales_data.sort_values(by='date')
                fig2, ax2 = plt.subplots(figsize=(8, 6))
                sns.lineplot(x='date', y='sales', data=sales_data, ax=ax2, palette="magma")
                ax2.set_title('Sales Over Time', fontsize=16)
                ax2.set_xlabel('Date', fontsize=12)
                ax2.set_ylabel('Sales', fontsize=12)
                st.pyplot(fig2)
        else:
            st.write("The query does not return a 'sales' column, which is required for metrics and some charts.")
    else:
        st.write("No data returned for the given query.")

    if st.button("Generate Insights"):
        with st.spinner("Generating insights..."):
            insights = generate_insights(sales_data)
            st.subheader("Generated Insights")
            st.write(insights)

else:
    st.info("Enter a SQL query to fetch data.")