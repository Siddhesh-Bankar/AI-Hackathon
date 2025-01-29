from crewai import CrewAI, Agent
from langchain_openai import AzureChatOpenAI
from crewai_tools import NL2SQLTool
import os
from dotenv import load_dotenv

load_dotenv()

default_llm = AzureChatOpenAI(
    openai_api_version=os.environ.get("AZURE_OPENAI_VERSION", "2023-07-01-preview"),
    azure_deployment=os.environ.get("AZURE_OPENAI_DEPLOYMENT", "gpt35"),
    azure_endpoint=os.environ.get("AZURE_OPENAI_ENDPOINT", "https://<your-endpoint>.openai.azure.com/"),
    api_key=os.environ.get("AZURE_OPENAI_KEY")
)

# Create a researcher agent
researcher = Agent(
  role='Senior Researcher',
  goal='Discover groundbreaking technologies',
  verbose=True,
  llm=default_llm,
  backstory='A curious mind fascinated by cutting-edge innovation and the potential to change the world, you know everything about tech.'
)

def create_agent():
    crewai = CrewAI(api_key="")
    agent = crewai.create_agent(
        name="SalesInsightsAgent",
        description="Analyzes sales data and automates tasks.",
    )

    return agent
