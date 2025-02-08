from crewai import Agent, Task, Crew, Process, LLM
from crewai_tools import NL2SQLTool
import os
import google.generativeai as genai
from langchain_google_genai import ChatGoogleGenerativeAI
from crewai import LLM
from crewai_tools import PDFSearchTool
import warnings
import re
from langchain_openai import AzureChatOpenAI
from tools.sendemail import SendEmailTool
warnings.simplefilter("ignore", ResourceWarning)


os.environ["OTEL_SDK_DISABLED"] = "true"

from dotenv import load_dotenv
load_dotenv()

os.environ["GOOGLE_API_KEY"] = "AIzaSyDSq_Lhr8Jt5Wvcd7Uh_VcmhlKyGDfq3uk"
genai.configure(api_key=os.environ["GOOGLE_API_KEY"])

def clean_query(query):
    if isinstance(query, str):
        # Remove backticks (`) and triple backticks (```)
        return re.sub(r'[`]+', '', query).strip()
    return query

def getInsights(query_input):
   
    
    llm = LLM(model="gemini/gemini-1.5-flash",api_key='AIzaSyDSq_Lhr8Jt5Wvcd7Uh_VcmhlKyGDfq3uk')

    # Create an agent that will use the NL2SQLTool
    insights_agent = Agent(
        role="Sales Insights Generator",
        goal="Generate insightful analysis from the sales data based on user queries.",
        backstory=(
        "I am an AI assistant trained to analyze sales data and generate actionable insights. I work primarily with the '[Intelligent4SPTeam].[sales_data]' "
        "and '[Intelligent4SPTeam].[product_data]' tables to extract meaningful patterns and trends. I am familiar with the structure of these tables, "
        "including key columns such as 'salesperson', 'region', 'product_id', 'sales', 'week', and 'month'. My goal is to provide "
        "users with relevant insights, such as identifying top-performing products, comparing sales across regions, or tracking sales "
        "trends over time. When asked for insights, I will analyze the data and ensure the results are actionable and easy to interpret. "
        "For example, if asked about the highest sales region in a specific month, I will query the data, summarize sales by region, "
        "and return the top performer. I understand that 'week' and 'month' are represented by integers, where '1' in the 'month' "
        "refers to January and '1' in the 'week' refers to the first week of the month. I aim to provide insights that help in "
        "strategic decision-making."
        ),
        llm=llm
    )

    # Define a task for the agent
    insights_task = Task(
        description="Generate actionable insights from the provided sales data based on the user query",
        agent=insights_agent,
        expected_output="A clear and meaningful insight based on the provided sales data, expressed in natural language.Generate actionable insights in table format."
        "give top salespersonmail and salesperson in heading as top salesperson and salespersonmail if applicable"
        "give insights with Bold text and emoji format"
    )


    # Create a Crew and execute the task
    crew = Crew(
        agents=[insights_agent],
        tasks=[insights_task]
    )

    email_agent = Agent(
        role="Sales Insights Generator",
        goal="Generate insightful analysis from the sales data based on user queries and send email reports.",
        backstory=(
            "I am an AI assistant trained to analyze sales data and generate actionable insights. "
        ),
        llm=llm,
        tools=[SendEmailTool()] 
    )

    email_task = Task(
        description="Send an email with the generated insights with",
        agent=email_agent,
        expected_output="Confirmation that the email was sent successfully."
    )

    email_crew = Crew(
            agents=[email_agent],
            tasks=[email_task],
            verbose=True
    )
    # Example usage
    insights_task.description = f"Give me some insights about the data: {query_input}"

    result = crew.kickoff()
    print(result)
    
    email_task.description = f"Send an email with the following insights: {result}"

    email_result = email_crew.kickoff()
    
    print(result)

    if hasattr(result, 'raw_output'):  
        nl2sqlquery = result.raw_output
    else:
        nl2sqlquery = str(result)  

    cleaned_result = clean_query(nl2sqlquery)
    return cleaned_result