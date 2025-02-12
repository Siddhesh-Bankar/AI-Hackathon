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
GOOGLE_API_KEY=st.secrets["GOOGLE_API_KEY"]

os.environ["GOOGLE_API_KEY"] = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=os.environ["GOOGLE_API_KEY"])

def clean_query(query):
    if isinstance(query, str):
        # Remove backticks (`) and triple backticks (```)
        return re.sub(r'[`]+', '', query).strip()
    return query

def getInsights(query_input):
   
    
    llm = LLM(model="gemini/gemini-1.5-flash",api_key=GOOGLE_API_KEY)

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
        role="Sales Insights Specialist",
        goal=(
            "To analyze complex sales data, identify key performance trends, and generate "
            "insightful reports that empower stakeholders to make informed business decisions. "
            "Deliver these insights through well-structured, professional email communications."
        ),
        backstory=(
            "I am a highly proficient AI-driven Sales Insights Specialist with deep expertise in "
            "data analytics and business intelligence. My primary responsibility is to transform "
            "raw sales data into meaningful and actionable insights. By leveraging advanced data "
            "analysis techniques, I extract key trends, uncover growth opportunities, and provide "
            "strategic recommendations. I ensure that all insights are communicated effectively "
            "through concise, data-driven email reports, enabling decision-makers to optimize "
            "sales strategies and drive business success."
        ),
        llm=llm,
        tools=[SendEmailTool()]
    )

# Define the email task
    email_task = Task(
        description=(
            "Draft and send a professional email containing data-driven sales insights. "
            "Ensure the email is structured, informative, and provides actionable takeaways "
            "that assist stakeholders in making strategic business decisions."
        ),
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
    
    email_task.description = f"Draft and send a professional email containing data-driven sales insights {result} .Ensure the email is structured, informative, and provides actionable takeaways that assist stakeholders in making strategic business decisions."

    email_result = email_crew.kickoff()
    
    print(result)

    if hasattr(result, 'raw_output'):  
        nl2sqlquery = result.raw_output
    else:
        nl2sqlquery = str(result)  

    cleaned_result = clean_query(nl2sqlquery)
    return cleaned_result