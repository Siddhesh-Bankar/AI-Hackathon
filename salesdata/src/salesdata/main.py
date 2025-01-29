import pandas as pd
from tools.custom_tool import fetch_sales_data, generate_insights,send_email
from tools.crew import create_agent

def main():
    # Initialize CrewAI agent
    agent = create_agent()

    # Fetch sales data
    query = "SELECT salesperson, region, product, sales, week, month FROM sales_data"
    sales_data = fetch_sales_data(query)

    # Generate insights
    insights = generate_insights(sales_data)
    print("Insights Generated:", insights)

    print(insights)
     # Send insights via email
    send_email(insights, attachment_path="sales_trends.png")

    result =  agent.complete_task("GenerateInsights", inputs={"sales_data": sales_data})
    print(result)
    # Automate email feedback
    agent.complete_task("SendKudosEmail", inputs={"insights": insights})

if __name__ == "__main__":
    main()



