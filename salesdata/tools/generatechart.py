from crewai import Agent, Task, Crew, Process
from crewai_tools import NL2SQLTool
import os
import google.generativeai as genai
from langchain_google_genai import ChatGoogleGenerativeAI
from crewai import LLM
from crewai_tools import PDFSearchTool
import warnings
import re
from langchain_openai import AzureChatOpenAI
from crewai_tools import DallETool
warnings.simplefilter("ignore", ResourceWarning)

os.environ["OTEL_SDK_DISABLED"] = "true"

from dotenv import load_dotenv

load_dotenv()

os.environ["OPENAI_API_KEY"] = os.getenv("AZURE_API_KEY")
os.environ["AZURE_API_KEY"] = os.getenv("AZURE_API_KEY")
os.environ["AZURE_API_BASE"] = os.getenv("AZURE_API_BASE")
os.environ["AZURE_API_VERSION"] = os.getenv("AZURE_API_VERSION")

def clean_query(query):
    if isinstance(query, str):
        # Remove backticks (`) and triple backticks (```)
        return re.sub(r'[`]+', '', query).strip()
    return query

def getCharts(query_input):
    # os.environ["GOOGLE_API_KEY"] = "4CAjxJRE4DzhhGdSTcDGj2inIkTFt3T9XqBrjVZiGDz6NaprvrUyJQQJ99BAACHYHv6XJ3w3AAAAACOGiLz5"
    # genai.configure(api_key=os.environ["OEN_API_KEY"])
    # llm = LLM(model="gemini/gemini-1.5-flash",api_key='AIzaSyDSq_Lhr8Jt5Wvcd7Uh_VcmhlKyGDfq3uk')
    # llm = LLM(model="gpt-4o-mini",api_key='4CAjxJRE4DzhhGdSTcDGj2inIkTFt3T9XqBrjVZiGDz6NaprvrUyJQQJ99BAACHYHv6XJ3w3AAAAACOGiLz5')
    llm = AzureChatOpenAI(
        azure_endpoint='https://prasa-m6jgverq-eastus2.cognitiveservices.azure.com/openai/deployments/gpt-4o-mini/chat/completions?api-version=2024-08-01-preview',
        api_key='4CAjxJRE4DzhhGdSTcDGj2inIkTFt3T9XqBrjVZiGDz6NaprvrUyJQQJ99BAACHYHv6XJ3w3AAAAACOGiLz5',
        deployment_name='gpt-4o-mini',
        model='azure/gpt-4o-mini',
        openai_api_type="azure",
        temperature=0,
        api_version='2024-08-01-preview',
        streaming=True,
        verbose=True
    )


    visualization_agent = Agent(
        role="Data Visualization Expert",
        goal="Generate visual representations (pie charts, bar charts) from the provided sales data",
        backstory=(
            "I am an AI assistant specialized in data visualization. My expertise lies in transforming raw sales data into "
            "intuitive and visually appealing charts, such as pie charts and bar charts. I work with the provided sales data "
            "to identify key trends, patterns, and comparisons."
            "data easy to understand through visual storytelling. I ensure that the charts are labeled clearly, use appropriate "
            "colors, and are accompanied by a brief explanation to highlight the key insights."
        ),
        llm=llm,
        tools=[DallETool()]
    )
    
    visualization_task = Task(
        description="Generate visual charts (pie charts, bar charts) from the provided sales data {description} based on the user query.",
        agent=visualization_agent,
        expected_output=(
            "A clear and visually appealing chart (pie chart or bar chart) based on the provided sales data"
        ),
        output_file='chart.png'
    )
    # Create a Crew and execute the task
    crew = Crew(
        agents=[visualization_agent],
        tasks=[visualization_task],
        process = Process.sequential,
    )

    # # Example usage
    visualization_task.description = f"Give me some insights about the data: {query_input}"

    result = crew.kickoff()
    
    if hasattr(result, 'raw_output'):  # If the attribute name is raw_output
        nl2sqlquery = result.raw_output
    else:
        nl2sqlquery = str(result)  # Fallback to string conversion

    # Clean up unwanted characters (remove backticks)
    cleaned_result = clean_query(nl2sqlquery)
    print(cleaned_result)
    return cleaned_result