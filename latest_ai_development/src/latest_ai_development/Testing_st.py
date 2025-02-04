import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from tools.custom_tool import fetch_sales_data, generate_insights, insert_data_into_database, authenticate_user
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
import smtplib
from tools.nl2sqltask import getnl2sqlQuery
from tools.insighttask import getInsights

# Set page config FIRST
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
    
    </style>
    """,
    unsafe_allow_html=True,
)
# Create login page using forms
def login():
    st.title("Login to Sales Data Insights! 🔑")

    # Create the form with a unique key
    with st.form(key="login_form"):
        # Input fields for username and password
        username = st.text_input("Username 👤")
        password = st.text_input("Password 🔒", type="password")
        
        # Create login button inside the form
        login_button = st.form_submit_button("Login ➡️")  # Form submission button
        

    # Handle the form submission when the login button is pressed
    if login_button:
        with st.spinner("Logging in..."):
            # Call authenticate_user to validate the username and password
            user_details = authenticate_user(username, password)
        
            if user_details:
                # Set session state to logged in
                st.session_state.logged_in = True
                st.session_state.username = user_details['username']  # Store the username in session state
                st.session_state.login_successful = True
                st.success(f"Welcome, {username}! 🎉")
                
                # This will auto-redirect to dashboard after login
                st.session_state.dashboard_redirect = True  # Set this flag
                st.rerun()  # Trigger a rerun to go to the dashboard
            else:
                st.session_state.login_successful = False
                st.error("Invalid username or password ❌") 

# Main Dashboard Page (Only visible after login)
def dashboard():
# Title and description
    # Title and description
    st.title("Sales Data Insights Chat")
    st.write("Chat with the app to explore and analyze your sales data with interactive charts, key metrics, and insightful summaries.")
    
    # Sidebar for SQL Query
    with st.sidebar:
        # Back to Login button
        if st.button("Back to Login 🔙"):
            # Reset session state to log out
            st.session_state.logged_in = False
            st.session_state.dashboard_redirect = False
            st.session_state.username = None
            st.session_state.login_successful = False
            st.session_state.sales_data = None  # Clear the sales data
            st.session_state.query = None  # Clear any query
            st.rerun()  # Rerun the app to show login page
        # Upload CSV and Insert into Database
        st.subheader("Upload CSV to Insert into Database 📥")
        uploaded_file = st.file_uploader("Choose a CSV file 📂", type="csv")

        if uploaded_file:
            csv_data = pd.read_csv(uploaded_file)
            st.subheader("Uploaded CSV Data 📊")
            st.dataframe(csv_data)

            # Button to insert CSV into database
            if st.button("Insert into Database 🗃️"):
                table_name = "sales_data"  # Replace with your target table name
                result_message = insert_data_into_database(csv_data, table_name)
                if "Successfully inserted" in result_message:
                    st.success(result_message + " ✅")
                else:
                    st.error(result_message + " ❌")

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

    # Automation: Send Email
    st.sidebar.subheader("Send Email Report 📄")
    email_to = st.sidebar.text_input("Recipient Email")
    email_subject = st.sidebar.text_input("Subject", "Sales Data Report")
    email_body = st.sidebar.text_area("Additional Body Content", "Here is the sales data report.")

    # Display Sales Data if available
    if "sales_data" in st.session_state and st.session_state.sales_data is not None:
        sales_data = st.session_state.sales_data
        if not sales_data.empty:
            st.subheader("Sales Data 📊")
            st.data_editor(sales_data, num_rows="dynamic")

            st.subheader("Key Metrics")
            if 'sales' in sales_data.columns:
                 # 🛠 Display Key Metrics
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Total Sales 💰", f"${sales_data['sales'].sum():,.2f}")
                with col2:
                    st.metric("Average Sales 💵", f"${sales_data['sales'].mean():,.2f}")
                with col3:
                    st.metric("Number of Transactions 🧮", len(sales_data))
                # Key Metrics
                total_sales = f"${sales_data['sales'].sum():,.2f} 💰"
                average_sales = f"${sales_data['sales'].mean():,.2f} 💵"
                num_transactions = len(sales_data)

                # 📊 Sales Analysis
                st.subheader("Sales Analysis")

                # Prepare inline image attachments
                sales_analysis_html = ""

                # Initialize chart paths to ensure they are always defined
                region_chart_path = ""
                time_chart_path = ""

                # Bar Chart: Sales by Region
                if 'region' in sales_data.columns and 'sales' in sales_data.columns:
                    fig1, ax1 = plt.subplots(figsize=(8, 6))
                    sns.barplot(x='region', y='sales', data=sales_data, ax=ax1, palette="viridis")
                    ax1.set_title('Sales by Region 📊', fontsize=16)
                    ax1.set_xlabel('Region 🌍', fontsize=12)
                    ax1.set_ylabel('Sales 💸', fontsize=12)
                    plt.xticks(rotation=45, ha='right')
                    st.pyplot(fig1)

                    # Save chart to file
                    region_chart_path = "sales_by_region.png"
                    fig1.savefig(region_chart_path, format="png")
                    sales_analysis_html += f'<h3>Sales by Region 📊</h3><img src="cid:sales_by_region.png"><br>'

                # Line Chart: Sales Over Time
                if 'date' in sales_data.columns and 'sales' in sales_data.columns:
                    sales_data['date'] = pd.to_datetime(sales_data['date'])
                    sales_data = sales_data.sort_values(by='date')
                    fig2, ax2 = plt.subplots(figsize=(8, 6))
                    sns.lineplot(x='date', y='sales', data=sales_data, ax=ax2, palette="magma")
                    ax2.set_title('Sales Over Time 📆', fontsize=16)
                    ax2.set_xlabel('Date 📅', fontsize=12)
                    ax2.set_ylabel('Sales 💵', fontsize=12)
                    st.pyplot(fig2)

                    # Save chart to file
                    time_chart_path = "sales_over_time.png"
                    fig2.savefig(time_chart_path, format="png")
                    sales_analysis_html += f'<h3>Sales Over Time ⏳</h3><img src="cid:sales_over_time.png"><br>'


            # Prepare Email Content
            if st.sidebar.button("Send Email 📧"):
                try:
                    # Set up email server
                    smtp_server = "smtp.gmail.com"
                    smtp_port = 587
                    smtp_user = "siddheshbankar16@gmail.com"
                    smtp_password = "oqzf mbwq mtqg wgad"

                    # Create email message
                    msg = MIMEMultipart("related")
                    msg["Subject"] = "Sales Data Report 📧"
                    msg["From"] = smtp_user
                    msg["To"] = email_to

                    # Email Body
                    html = f"""
                    <html>
                    <body>
                        <h1>Sales Data Report 📧</h1>
                        <p>{email_body} 📊</p>
                        <h2>Key Metrics 💰</h2>
                        <ul>
                            <li><strong>Total Sales 💵:</strong> {total_sales}</li>
                            <li><strong>Average Sales 💵:</strong> {average_sales}</li>
                            <li><strong>Number of Transactions 🧮:</strong> {num_transactions}</li>
                        </ul>
                        <h2>Sales Data 📊</h2>
                        {sales_data.to_html(index=False)}
                        <h2>Sales Analysis 📊</h2>
                        {sales_analysis_html}
                    </body>
                    </html>
                    """
                    msg.attach(MIMEText(html, "html"))

                    # Attach images inline
                    for cid, path in [("sales_by_region.png", region_chart_path), ("sales_over_time.png", time_chart_path)]:
                        with open(path, "rb") as img_file:
                            img = MIMEImage(img_file.read())
                            img.add_header("Content-ID", f"<{cid}>")
                            img.add_header("Content-Disposition", "inline", filename=cid)
                            msg.attach(img)

                    # Send the email
                    with smtplib.SMTP(smtp_server, smtp_port) as server:
                        server.starttls()
                        server.login(smtp_user, smtp_password)
                        server.sendmail(smtp_user, email_to, msg.as_string())

                    st.sidebar.success("Email sent successfully! 📧")
                except Exception as e:
                    st.sidebar.error(f"Error: {str(e)} ❌")

        if st.button("Generate Insights"):
            with st.spinner("Generating insights..."):
                insights = generate_insights(sales_data)
                insightsfromcrew=getInsights(sales_data)
                st.subheader("Generated Insights")
                st.write(insights)
                st.subheader("Generated Insights from crew ai")
                st.write(insightsfromcrew)

    # else:
    #     st.info("Enter a SQL query to fetch data 📊.")


# Application Flow
if "logged_in" not in st.session_state or not st.session_state.logged_in:
    login()
elif st.session_state.get("dashboard_redirect", False):
    # If the user is logged in, we automatically show the dashboard
    dashboard()
else:
    # Prompt login or signup
    st.warning("Please log in to access the dashboard ⚠️.")
