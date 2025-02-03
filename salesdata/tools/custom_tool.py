import pandas as pd
import pyodbc
from matplotlib import pyplot as plt
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import os
import psycopg2
import pymssql

def connect_to_sql_server():
    conn = pymssql.connect(
        server='arieotechdb.database.windows.net',  # Replace with your SQL Server host
        user='Intelligent4SPTeam',  # Replace with your SQL Server username
        password='6xLVPIauw9YNFdv',  # Replace with your SQL Server password
        database='Hackathon-Master-Database'  # Replace with your database name
    )
    return conn

    

def fetch_sales_data(query):
    conn = connect_to_sql_server()
    df = pd.read_sql(query, conn)
    conn.close()
    return df

def generate_insights(sales_data):
    weekly_trend = sales_data.groupby("week")["sales"].sum()
    monthly_trend = sales_data.groupby("month")["sales"].sum()

    plt.figure(figsize=(10, 6))
    plt.plot(weekly_trend, label="Weekly Sales")
    plt.plot(monthly_trend, label="Monthly Sales")
    plt.legend()
    plt.title("Sales Trends")
    plt.savefig("sales_trends.png")
    return {"weekly_trend": weekly_trend, "monthly_trend": monthly_trend}

def send_email(insights, attachment_path):
    """
    Send an email with sales insights and a graph attachment.
    """
    sender_email = "shelarpooja21@gmail.com"  # Replace with your email
    receiver_email = "shelarpooja21@gmail.com"  # Replace with recipient email
    subject = "Weekly and Monthly Sales Insights"
    smtp_server = "smtp.gmail.com"  # Replace with your SMTP server
    smtp_port = 587
    email_password = "Pooja@2104"  # Replace with your email password

    # Email content
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = subject

    # Email body
    body = f"""
    Hi Team,

    Please find the sales insights below:

    Weekly Sales Trend:
    {insights['weekly_trend']}

    Monthly Sales Trend:
    {insights['monthly_trend']}

    The sales trends graph is attached for reference.

    Best Regards,
    Sales Analytics Team
    """
    message.attach(MIMEText(body, "plain"))

    # Attach the graph
    if os.path.exists(attachment_path):
        with open(attachment_path, "rb") as attachment:
            part = MIMEBase("application", "octet-stream")
            part.set_payload(attachment.read())
        encoders.encode_base64(part)
        part.add_header("Content-Disposition", f"attachment; filename={os.path.basename(attachment_path)}")
        message.attach(part)

    # Send the email
    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(sender_email, email_password)
        server.sendmail(sender_email, receiver_email, message.as_string())
        print("Email sent successfully!")
    except Exception as e:
        print(f"Failed to send email: {e}")
    finally:
        server.quit()


