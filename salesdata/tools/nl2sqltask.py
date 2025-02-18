from crewai import Agent, Task, Crew
from crewai_tools import NL2SQLTool
import os
import google.generativeai as genai
from langchain_google_genai import ChatGoogleGenerativeAI
from crewai import LLM
from crewai_tools import PDFSearchTool
import warnings
import re
from langchain_openai import AzureChatOpenAI
warnings.simplefilter("ignore", ResourceWarning)

os.environ["OTEL_SDK_DISABLED"] = "true"

from dotenv import load_dotenv

load_dotenv()

# os.environ["OPENAI_API_KEY"] = os.getenv("AZURE_API_KEY")
# os.environ["AZURE_API_KEY"] = os.getenv("AZURE_API_KEY")
# os.environ["AZURE_API_BASE"] = os.getenv("AZURE_API_BASE")
# os.environ["AZURE_API_VERSION"] = os.getenv("AZURE_API_VERSION")

os.environ["GOOGLE_API_KEY"] = "AIzaSyDSq_Lhr8Jt5Wvcd7Uh_VcmhlKyGDfq3uk"
genai.configure(api_key=os.environ["GOOGLE_API_KEY"])

def clean_query(query):
    if isinstance(query, str):
        # Remove backticks (`) and triple backticks (```)
        return re.sub(r'[`]+', '', query).strip()
    return query

def getnl2sqlQuery(query_input):
   
    llm = LLM(model="gemini/gemini-1.5-flash",api_key='AIzaSyDSq_Lhr8Jt5Wvcd7Uh_VcmhlKyGDfq3uk')
    # llm = AzureChatOpenAI(
    #     azure_endpoint='https://prasa-m6jgverq-eastus2.cognitiveservices.azure.com/openai/deployments/gpt-4o-mini/chat/completions?api-version=2024-08-01-preview',
    #     api_key='4CAjxJRE4DzhhGdSTcDGj2inIkTFt3T9XqBrjVZiGDz6NaprvrUyJQQJ99BAACHYHv6XJ3w3AAAAACOGiLz5',
    #     deployment_name='gpt-4o-mini',
    #     model='azure/gpt-4o-mini',
    #     openai_api_type="azure",
    #     temperature=0.8,
    #     max_tokens=4096,
    #     api_version='2024-08-01-preview',
    #     streaming=True,
    #     verbose=True
    # )
   
    # Initialize the NL2SQLTool with your database URI
    nl2sql = NL2SQLTool(db_uri="mssql+pymssql://Intelligent4SPTeam:6xLVPIauw9YNFdv@arieotechdb.database.windows.net/Hackathon-Master-Database")

    # Create an agent that will use the NL2SQLTool
    # Create an agent that will use the NL2SQLTool
    sql_agent = Agent(
        role="SQL Query Generator",
        goal="Convert natural language queries into precise SQL queries for the sales_data table, ensuring accurate and efficient querying. If the query is a formal question like 'Hi', 'Hello', or 'Who are you', respond appropriately without generating an SQL query.",
        backstory=(
            "I am an AI assistant skilled in transforming natural language queries into structured SQL statements, specifically "
            "designed to work with the '[Intelligent4SPTeam].[sales_data]' and '[Intelligent4SPTeam].[product_data]' tables. I understand the structure of these tables, "
            "including columns like salesperson, region, product_id, sales, week, and month. My primary goal is to provide "
            "accurate, data-driven insights based on user input, ensuring all queries are well-formed and precise. "
            "In the 'sales_data' table, 'product_id' is used as a reference to the 'product_data' table, where I can retrieve "
            "detailed information about each product, such as its name, price, expiry_date and manufacturer."
            "When you ask for insights like the 'highest sales product last month,' I will query the sales data, identify the "
            "product using 'product_id,' and return the corresponding product details such as the product name from the 'product_data' table. "
            "For example, I know that 1 corresponds to January, 2 corresponds to February, and so on up to December. "
            "The 'week' column contains integer values where 1 corresponds to the first week of the month, and so on. "
            "I will always ensure the results are user-friendly and return meaningful data like the product_name instead of just IDs."
            "If the user asks a formal question like 'Hi', 'Hello', or 'Who are you', I will respond appropriately without generating an SQL query."
        ),
        tools=[nl2sql],
        llm=llm
    )

    # Define a task for the agent
    query_task = Task(
        description="Convert the following natural language query to SQL. If the query is a formal question like 'Hi', 'Hello', or 'Who are you', respond appropriately without generating an SQL query.",
        agent=sql_agent,
        expected_output=(
            "If the query is a formal question, return an appropriate response like 'Hello! How can I assist you with SQL queries today?' "
            "If the query is a valid natural language question, return a valid SQL query in string format without the SQL keyword. "
            "Ensure the SQL query is well-formed and references the '[Intelligent4SPTeam].[sales_data]' and '[Intelligent4SPTeam].[product_data]' tables."
        )
    )

    # Create a Crew and execute the task
    crew = Crew(
        agents=[sql_agent],
        tasks=[query_task]
    )

    # Example usage
    user_query = query_input

    # Set the task description with the user query
    query_task.description = f"Convert the following natural language query to SQL: {user_query}"

    # Execute the task
    result = crew.kickoff()

    # Extract the actual output from the CrewOutput object
    if hasattr(result, 'raw_output'):  # If the attribute name is raw_output
        output = result.raw_output
    else:
        output = str(result)  # Fallback to string conversion

    # Clean up unwanted characters (e.g., remove backticks)
    cleaned_result = clean_query(output)
    print(cleaned_result)
    return cleaned_result