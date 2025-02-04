import pyodbc
import pandas as pd
from typing import Type
from pydantic import BaseModel, Field
from crewai.tools import BaseTool
from matplotlib import pyplot as plt

class MyCustomToolInput(BaseModel):
    """Input schema for MyCustomTool."""
    argument: str = Field(..., description="Description of the argument.")

class MyCustomTool(BaseTool):
    name: str = "Name of my tool"
    description: str = "Clear description for what this tool is useful for, your agent will need this information to use it."
    args_schema: Type[BaseModel] = MyCustomToolInput

    def _run(self, argument: str) -> str:
        return "this is an example of a tool output, ignore it and move along."
    
def connect_to_sql_server():
    """Establishes a connection to the SQL Server database."""
    try:
        # conn = pyodbc.connect(
        #     "DRIVER={ODBC Driver 17 for SQL Server};"
        #     "SERVER=localhost;"  # Change this if you're using a different server
        #     "DATABASE=Events;"  # Replace with your actual database name
        #     "Trusted_Connection=yes;"  # Ensure this is correct for your authentication type
        # )
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
    """Fetch sales data from the database based on the provided SQL query."""
    conn = connect_to_sql_server()
    if conn:
        df = pd.read_sql(query, conn)
        conn.close()
        return df
    else:
        raise Exception("Could not connect to the database.")

def insert_data_into_database(dataframe, table_name):
    """Inserts a Pandas DataFrame into the specified SQL Server table."""
    try:
        conn = connect_to_sql_server()
        cursor = conn.cursor()

        # Dynamically generate the INSERT query
        columns = ", ".join(dataframe.columns)
        placeholders = ", ".join(["?"] * len(dataframe.columns))
        query = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"

        # Convert DataFrame rows to tuples for execution
        data = [tuple(row) for row in dataframe.to_numpy()]

        # Execute the query for each row
        cursor.executemany(query, data)
        conn.commit()
        conn.close()

        return f"Successfully inserted {len(dataframe)} rows into the table '{table_name}'."
    except Exception as e:
        return f"Error inserting data: {str(e)}"

def generate_insights(sales_data):
    """Generate insights based on sales data."""
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
        query = "SELECT username, password FROM users WHERE username = ? AND password = ?"
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

def create_user(username, password, email):
    """Create a new user in the database."""
    try:
        conn = connect_to_sql_server()
        cursor = conn.cursor()

        # Query to insert a new user into the users table
        query = "INSERT INTO users (username, password, email) VALUES (?, ?, ?)"
        cursor.execute(query, (username, password, email))
        conn.commit()
        conn.close()
        print(f"User {username} created successfully.")
    except Exception as e:
        print(f"Error creating user: {str(e)}")
