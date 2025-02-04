import streamlit as st
from langchain.llms import OpenAI
from langchain.chains import SQLDatabaseChain
from langchain.sql_database import SQLDatabase
from sqlalchemy import create_engine
import smtplib
from email.mime.text import MIMEText

 
# Configure OpenAI API Key
OPENAI_API_KEY = "your_openai_api_key_here"
 
# Database Connection (MySQL example)
DB_URI = "mysql+pymysql://username:password@localhost/sales_db"
engine = create_engine(DB_URI)
db = SQLDatabase(engine)
 
# Initialize LangChain
llm = OpenAI(temperature=0, openai_api_key=OPENAI_API_KEY)
db_chain = SQLDatabaseChain(llm=llm, database=db, verbose=True)
 
# Streamlit UI
st.title("Sales Data Insights")
st.sidebar.header("Options")
query = st.text_area("Ask a question about sales data (e.g., 'Show sales by region'):")
 
if st.button("Run Query"):
    try:
        # Use LangChain to generate SQL and execute
        result = db_chain.run(query)
        st.success("Query executed successfully!")
        st.write(result)
    except Exception as e:
        st.error(f"Error: {str(e)}")
 
# Automation: Send Email
st.sidebar.subheader("Send Email Report")
email_to = st.sidebar.text_input("Recipient Email")
email_subject = st.sidebar.text_input("Subject", "Sales Data Report")
email_body = st.sidebar.text_area("Body", "Here is the sales data report.")
 
if st.sidebar.button("Send Email"):
    try:
        # Set up email server
        smtp_server = "smtp.your-email-provider.com"
        smtp_port = 587
        smtp_user = "your_email@example.com"
        smtp_password = "your_email_password"
 
        msg = MIMEText(email_body)
        msg["Subject"] = email_subject
        msg["From"] = smtp_user
        msg["To"] = email_to
 
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(smtp_user, smtp_password)
            server.sendmail(smtp_user, email_to, msg.as_string())
 
        st.sidebar.success("Email sent successfully!")
    except Exception as e:
        st.sidebar.error(f"Error: {str(e)}")