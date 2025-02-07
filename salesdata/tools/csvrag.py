# from crewai import Agent, Task, Crew, Process, LLM
# from crewai_tools import NL2SQLTool
# import os
# import google.generativeai as genai
# from langchain_google_genai import ChatGoogleGenerativeAI
# from crewai import LLM
# from crewai_tools import PDFSearchTool
# import warnings
# import re
# from langchain_openai import AzureChatOpenAI
# from crewai_tools import CSVSearchTool
# import time
# warnings.simplefilter("ignore", ResourceWarning)

# os.environ["OTEL_SDK_DISABLED"] = "true"

# from dotenv import load_dotenv

# load_dotenv()

# os.environ["GOOGLE_API_KEY"] = "AIzaSyDSq_Lhr8Jt5Wvcd7Uh_VcmhlKyGDfq3uk"
# genai.configure(api_key=os.environ["GOOGLE_API_KEY"])

# tool = CSVSearchTool(csv=r'salesdata\tools\Book 26(Sheet1).csv')

# def clean_query(query):
#     if isinstance(query, str):
#         # Remove backticks (`) and triple backticks (```)
#         return re.sub(r'[`]+', '', query).strip()
#     return query

# def stream_result(formatted_output):
#     output_parts = formatted_output.split("\n")
    
#     for part in output_parts:
#         yield part + "\n"
#         time.sleep(0.5)  # Simulate a delay between each chunk to mimic streaming

# def getCSVInsights():
#     # os.environ["GOOGLE_API_KEY"] = "4CAjxJRE4DzhhGdSTcDGj2inIkTFt3T9XqBrjVZiGDz6NaprvrUyJQQJ99BAACHYHv6XJ3w3AAAAACOGiLz5"
#     # genai.configure(api_key=os.environ["OEN_API_KEY"])

#     llm = LLM(model="gemini/gemini-1.5-flash",api_key='AIzaSyDSq_Lhr8Jt5Wvcd7Uh_VcmhlKyGDfq3uk')
#     # llm = AzureChatOpenAI(
#     #     azure_endpoint='https://prasa-m6jgverq-eastus2.cognitiveservices.azure.com/openai/deployments/gpt-4o-mini/chat/completions?api-version=2024-08-01-preview',
#     #     api_key='4CAjxJRE4DzhhGdSTcDGj2inIkTFt3T9XqBrjVZiGDz6NaprvrUyJQQJ99BAACHYHv6XJ3w3AAAAACOGiLz5',
#     #     deployment_name='gpt-4o-mini',
#     #     model='azure/gpt-4o-mini',
#     #     openai_api_type="azure",
#     #     temperature=0,
#     #     api_version='2024-08-01-preview',
#     #     streaming=True,
#     #     verbose=True
#     # )

#     # Create an agent that will use the NL2SQLTool
#     # Define the agent for analyzing CSV data
#     # Define the agent for analyzing CSV sales data
#     csv_sales_analysis_agent = Agent(
#         role="Sales Data Analyzer",
#         goal="Generate actionable insights from the provided sales data based on user queries.",
#         backstory=(
#             "I am an AI assistant trained to analyze sales data from CSV files. I work with data that includes columns like 'Salesperson', 'Region', 'Sales', "
#             "'Product', 'Sales Value', 'Email', 'Category', 'Date', and more. My goal is to help users gain insights such as identifying top salespeople, "
#             "trends over time, and performance by region or product. For example, if asked about the top-performing salesperson, I will analyze total sales "
#             "per salesperson and return the best performer. I also can generate insights about sales trends by region or product, or identify which product "
#             "category had the most sales in a given period. I will ensure all insights are actionable and easy to understand, enabling better decision-making."
#         ),
#         llm=llm,
#         tools=[tool]
#     )


#     # Define tasks for the agent
#     task_1 = Task(
#     description="Identify the top salesperson based on total sales.",
#     agent=csv_sales_analysis_agent,
#     expected_output=(
#         "**Top Salesperson** 👑\n\n"
#         "🏆 **Name**: John Doe\n"
#         "💰 **Total Sales**: **$15,000.00**\n"
#         "📧 **Email**: johndoe@example.com\n\n"
#         "_**Great job John! Keep up the amazing work!**_ 💪"
#     )
#     )



#     task_2 = Task(
#     description="Analyze sales trends by region, identifying which region had the highest total sales over the last quarter.",
#     agent=csv_sales_analysis_agent,
#     expected_output=(
#         "**Sales Performance by Region** 🌍\n\n"
#         "**North**: **$7,000.00** 💵\n"
#         "**South**: **$9,800.00** 💵\n"
#         "**East**: **$8,700.00** 💵\n"
#         "**West**: **$6,000.00** 💵\n\n"
#         "🌟 **Top Region: South** with **$9,800.00** 💰📈\n\n"
#         "_**Excellent performance by South region!**_ 🏅"
#     )
# )


# #     task_3 = Task(
# #     description="Identify the top-selling product based on total sales.",
# #     agent=csv_sales_analysis_agent,
# #     expected_output=(
# #         "**Top-Selling Product** 🏆\n\n"
# #         "📦 **Product**: Aspirin\n"
# #         "💰 **Total Sales**: **$15,000.00** 💵\n"
# #         "🛒 **Sales by Region**: North, South, East, West\n\n"
# #         "_**Aspirin is leading the sales charts!**_ 💥"
# #     )
# # )

#     # Create a Crew and execute the task
#     crew = Crew(
#         agents=[csv_sales_analysis_agent],
#         tasks=[task_1,task_2],
#         Process=Process.sequential
     
#     )

#     # Example usage

#     result = crew.kickoff()
    
#     print(result)
#     # Extract the actual SQL query from the CrewOutput object
#     if hasattr(result, 'raw'):  # If the attribute name is raw_output
#         nl2sqlquery = result.raw
#     else:
#         nl2sqlquery = str(result)  # Fallback to string conversion

#     # Clean up unwanted characters (remove backticks)
#     cleaned_result = clean_query(nl2sqlquery)
#      # Output each chunk progressively to simulate streaming

#     return cleaned_result  # Return the final cleaned result