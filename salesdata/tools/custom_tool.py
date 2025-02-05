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

def connect_to_sql_server():
    """Establishes a connection to the SQL Server database."""
    try:
        conn = pyodbc.connect(
            "DRIVER={ODBC Driver 17 for SQL Server};"
            "SERVER=arieotechdb.database.windows.net;"  
            "DATABASE=Hackathon-Master-Database;"  
            "UID=Intelligent4SPTeam;"  
            "PWD=6xLVPIauw9YNFdv;" 
        )
        return conn
    except Exception as e:
        print(f"Error connecting to SQL Server: {e}")
        return None    

def fetch_sales_data(query):
    conn = connect_to_sql_server()
    df = pd.read_sql(query, conn)
    conn.close()
    return df

def insert_data_into_database(dataframe, table_name):
    """Inserts a Pandas DataFrame into the specified SQL Server table."""
    try:
        conn = connect_to_sql_server()
        cursor = conn.cursor()

        columns = ", ".join(dataframe.columns)
        placeholders = ", ".join(["?"] * len(dataframe.columns))
        query = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"

        data = [tuple(row) for row in dataframe.to_numpy()]

        cursor.executemany(query, data)
        conn.commit()
        conn.close()

        return f"Successfully inserted {len(dataframe)} rows into the table '{table_name}'."
    except Exception as e:
        return f"Error inserting data: {str(e)}"

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

def authenticate_user(username, password):
    """Authenticate a user against the 'users' table in the database."""
    try:
        conn = connect_to_sql_server()
        cursor = conn.cursor()

        # Query to fetch user details based on username and password
        query = "SELECT username, password FROM Intelligent4SPTeam.users WHERE username = ? AND password = ?"
        cursor.execute(query, (username, password))
        user = cursor.fetchone()
        conn.close()

        if user:  # If the user exists in the database
            return {"username": user[0]}  # Return the username (or any other user details)
        else:
            return None  # No matching user found
    except Exception as e:
        print(f"Error authenticating user: {str(e)}")
        return None



