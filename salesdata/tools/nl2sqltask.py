from crewai import Agent, Task, Crew
from crewai_tools import NL2SQLTool
import os
import google.generativeai as genai
from langchain_google_genai import ChatGoogleGenerativeAI
from crewai import LLM
from crewai_tools import PDFSearchTool
import warnings
import re
warnings.simplefilter("ignore", ResourceWarning)

def clean_query(query):
    if isinstance(query, str):
        # Remove backticks (`) and triple backticks (```)
        return re.sub(r'[`]+', '', query).strip()
    return query

def getnl2sqlQuery(query_input):
    os.environ["GOOGLE_API_KEY"] = "AIzaSyDUwyyNh6Yg50MveTLWmEQLl7NhwB6s7xA"
    genai.configure(api_key=os.environ["GOOGLE_API_KEY"])

    llm = LLM(model="gemini/gemini-1.5-flash",api_key='AIzaSyDUwyyNh6Yg50MveTLWmEQLl7NhwB6s7xA')
    # Initialize the NL2SQLTool with your database URI
    nl2sql = NL2SQLTool(db_uri="postgresql://postgres:admin@localhost:5432/test")

    # Create an agent that will use the NL2SQLTool
    sql_agent = Agent(
        role="SQL Query Generator",
        goal="Convert natural language queries into precise SQL queries for the sales_data table, ensuring accurate and efficient querying.",
        backstory=(
            "I am an AI assistant skilled in transforming natural language queries into structured SQL statements, specifically "
            "designed to work with the 'sales_data' table. I understand the structure of the table, including columns like "
            "salesperson, region, product, sales, week, and month, and can generate SQL queries that return meaningful insights. "
            "where 1 corresponds to January, 2 corresponds to February, and so on up to December. The 'week' column contains "
            "integer values, where 1 corresponds to the first week of the month, 2 corresponds to the second week, and so on. "
            "week and month contains integer indicating or "
            "My goal is to provide accurate results based on user input, ensuring all queries are well-formed and precise."
        ),
        tools=[nl2sql],
        llm=llm
    )


    # Define a task for the agent
    query_task = Task(
        description="Convert the following natural language query to SQL",
        agent=sql_agent,
        expected_output="A valid SQL query give strict in string format only without the sql keyword",
        llm=llm
    )

    # Create a Crew and execute the task
    crew = Crew(
        agents=[sql_agent],
        tasks=[query_task]
    )

    # Example usage
    user_query = query_input

    query_task.description = f"Convert the following natural language query to SQL: {user_query}"
    print(user_query)
    result = crew.kickoff()
     # Extract the actual SQL query from the CrewOutput object
    if hasattr(result, 'raw_output'):  # If the attribute name is raw_output
        nl2sqlquery = result.raw_output
    else:
        nl2sqlquery = str(result)  # Fallback to string conversion

    # Clean up unwanted characters (remove backticks)
    cleaned_result = clean_query(nl2sqlquery)
    print(cleaned_result)
    return cleaned_result