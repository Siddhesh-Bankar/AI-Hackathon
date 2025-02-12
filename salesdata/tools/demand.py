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
import json
import streamlit as st

os.environ["OTEL_SDK_DISABLED"] = "true"

from dotenv import load_dotenv
load_dotenv()

os.environ["GOOGLE_API_KEY"] = st.secrets["GOOGLE_API_KEY"]
genai.configure(api_key=os.environ["GOOGLE_API_KEY"])

def clean_query(query):
    if isinstance(query, str):
        # Remove backticks (`) and triple backticks (```)
        return re.sub(r'[`]+', '', query).strip()
    return query

def getDemandJson(query_input):
   
    
    llm = LLM(model="gemini/gemini-1.5-flash",api_key='AIzaSyDSq_Lhr8Jt5Wvcd7Uh_VcmhlKyGDfq3uk')

    # Create an agent that will use the NL2SQLTool
    sales_data_converter_agent = Agent(
        role="Sales Data array Converter",
        goal="Convert structured sales data into a well-formatted array representation.",
        backstory=(
            "I am an AI assistant specialized in transforming structured sales data into array format. I work with tabular data such as CSV files, SQL query results, "
            "or Pandas DataFrames and ensure that the data is properly structured, validated, and formatted as array. My primary responsibility is to preserve data integrity, "
            "handle missing values, and generate an optimized array output suitable for downstream processing or API consumption. "
            "I understand various data structures, including sales transactions, product details, and customer records, and can adapt the output format as needed. "
            "If any data inconsistencies arise, I will apply appropriate cleansing techniques before conversion."
        ),
        llm=llm
    )

    # Define a task for the agent
    convert_sales_data_task = Task(
            description="Transform the given sales data into a structured array format, ensuring data integrity and correctness.",
            agent=sales_data_converter_agent,
            expected_output=(
                "A valid array representing the provided sales data, ensuring correct field mappings and handling of missing values"
               """
               "products": [
                        {"product_name": "Product A", "manufacturer": "Company X",TotalSales:"100.00", "quantity": "10" },
                        {"product_name": "Product B", "manufacturer": "Company X",TotalSales:"100.00", "quantity": "10" },
                        {"product_name": "Product C", "manufacturer": "Company X",TotalSales:"100.00", "quantity": "10" },
                        {"product_name": "Product D", "manufacturer": "Company X",TotalSales:"100.00", "quantity": "10" },
                        {"product_name": "Product E", "manufacturer": "Company X",TotalSales:"100.00", "quantity": "10" }
                    ]
                
                """
            )
    )

    # Create a Crew and execute the task
    crew = Crew(
        agents=[sales_data_converter_agent],
        tasks=[convert_sales_data_task]
    )

    
    convert_sales_data_task.description = f"Convert structured sales data into a well-formatted array representation.: {query_input}"

    result = crew.kickoff()
    print(type(result.raw))
    print(result)
    import re

# Remove potential Markdown-style JSON formatting artifacts
    fixed_json = re.sub(r'```json\n|\n```', '', result.raw).strip()

    data = json.loads(fixed_json)
    print(data)


# Extract the products array
    products = data.get("products", [])
    return products