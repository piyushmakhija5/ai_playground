import os
from dotenv import load_dotenv
from crewai import Agent, Task, Crew, Process
import pandas as pd
import json

load_dotenv()

# Define your agents (excluding report_generation_agent for now)

credit_decision_manager = Agent(
    role='Credit Decision Manager',
    goal='Oversee the credit assessment process and interface with customers',
    backstory="""You are the customer-facing representative and orchestrator of the credit underwriting team.
You ensure that client needs are met and coordinate the workflow among the team members.
You have a deep understanding of the key terms and dataset structure provided, and you make sure the team interprets the data exactly as specified.""",
    verbose=True,
    allow_delegation=True
)

data_ingestion_analyst = Agent(
    role='Data Ingestion and Analyst Agent',
    goal='Analyze preprocessed financial data to prepare signals for creditworthiness determination',
    backstory="""You specialize in handling financial data that has been preprocessed.
You interpret the provided data exactly as specified and extract relevant features and insights for credit assessment.""",
    verbose=True,
    allow_delegation=False
)

credit_risk_assessment = Agent(
    role='Credit Risk Assessment Agent',
    goal='Evaluate the creditworthiness of entities using precise financial metrics and credit scoring models',
    backstory="""You are an expert in financial analysis and risk modeling.
You use the provided metrics to assess credit risk accurately.
You understand the specific data and how it impacts credit risk.
You will prepare an overall assessment, including a score out of 10, focusing on what qualifies or disqualifies the business as credit-worthy.""",
    verbose=True,
    allow_delegation=False
)

qa_agent = Agent(
    role='Quality Assurance Agent',
    goal='Ensure all calculations and analyses are 100% accurate and reliable',
    backstory="""You meticulously review outputs from other agents.
Your attention to detail ensures that all findings are precise before they are finalized.
You verify that the data interpretations and calculations adhere exactly to the specified dataset structure and key terms.
Confirm that the final report meets the formatting and content requirements.""",
    verbose=True,
    allow_delegation=False
)

# Define the key terms and dataset structure

key_terms_and_structure = """
Key Terms:
- GST: Tax on goods/services, varies by category.
- Excl GST: Cost without GST.

Dataset Structure:
1. Order Id: Unique per order.
2. SKU ID: Unique product identifier.
3. Product Category: Grouping of SKUs based on type of product.
4. Order Date: DD-MM-YY format.
5. Order Status: 'delivered', 'returned', 'free_replacement' (treat 'free_replacement' as 'returned' unless specified).
6. Listing Gmv: Gross value, before discount.
7. Shipping Discount
8. Self Discount
9. Total Discount: Sum of Shipping and Self Discount.
10. Net Sales Excl Gst: This is the effective total sale for each order.
11. Delivered Charges Excl Gst
12. Returned Charges Excl Gst
13. Free Replacement Charges Excl Gst (part of returned order charges unless specified).
14. Indirect Charges Excl Gst
15. Net Revenue Excl Gst: This is the final revenue or profit we are making from the sale.
16. Output Gst: GST/Tax liability for us.
17. Input Credit Gst: Reduction in our GST/Tax liability.
18. TCS: Tax Collected at Source at the time of sale.
19. TDS: Tax Deducted at Source (refundable if order is returned).

Column Relations:
- Total Discount = Self Discount + Shipping Discount
- Returned Charges Excl Gst = Free Replacement Charges Excl Gst + other return charges
- Total Tax liability = Output Gst - Input Credit Gst
- Total Charges/Fee (Cost of Doing Business on marketplace) = Delivered Charges Excl Gst + Returned Charges Excl Gst + Free Replacement Charges Excl Gst + Indirect Charges Excl Gst
- Total Profit = Net Sales Excl Gst - Net Revenue Excl Gst
- Biggest/Largest Charge/Fee: Charge or fee with the highest absolute value.
"""

# Function to preprocess and analyze the financial data

def preprocess_financial_data(csv_file_path):
    # Load the data
    df = pd.read_excel(csv_file_path)

    # Ensure correct data types
    numeric_columns = [
        'Shipping Discount', 'Self Discount', 'Total Discount', 'Net Sales Excl Gst',
        'Delivered Charges Excl Gst', 'Returned Charges Excl Gst',
        'Free Replacement Charges Excl Gst', 'Indirect Charges Excl Gst',
        'Net Revenue Excl Gst', 'Output Gst', 'Input Credit Gst',
        'Listing Gmv'
    ]
    for col in numeric_columns:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

    # Calculate Total Discount if not present
    if 'Total Discount' not in df.columns or df['Total Discount'].isnull().all():
        df['Total Discount'] = df['Self Discount'] + df['Shipping Discount']

    # Calculate Total Tax liability
    df['Total Tax liability'] = df['Output Gst'] - df['Input Credit Gst']

    # Calculate Total Charges/Fee
    df['Total Charges/Fee'] = (
        df['Delivered Charges Excl Gst'] +
        df['Returned Charges Excl Gst'] +
        df['Free Replacement Charges Excl Gst'] +
        df['Indirect Charges Excl Gst']
    )

    # Calculate Total Profit
    df['Total Profit'] = df['Net Sales Excl Gst'] - df['Net Revenue Excl Gst']

    # Identify the Biggest/Largest Charge/Fee
    charges_cols = [
        'Delivered Charges Excl Gst',
        'Returned Charges Excl Gst',
        'Free Replacement Charges Excl Gst',
        'Indirect Charges Excl Gst'
    ]
    df['Biggest Charge/Fee'] = df[charges_cols].abs().max(axis=1)

    # Summarize the data
    summary = {
        'Total Discount Sum': df['Total Discount'].sum(),
        'Total Tax Liability Sum': df['Total Tax liability'].sum(),
        'Total Charges/Fee Sum': df['Total Charges/Fee'].sum(),
        'Total Profit Sum': df['Total Profit'].sum(),
        'Average Biggest Charge/Fee': df['Biggest Charge/Fee'].mean(),
        'Total Net Sales Excl Gst': df['Net Sales Excl Gst'].sum(),
        'Total Net Revenue Excl Gst': df['Net Revenue Excl Gst'].sum(),
        'Total Listing Gmv': df['Listing Gmv'].sum(),
        'Total Orders': len(df),
        # Add more summary metrics as needed
    }

    # Return the preprocessed data and summary
    return df, summary

# Function to escape curly braces in strings
def escape_curly_braces(s):
    return s.replace('{', '{{').replace('}', '}}')

if __name__ == "__main__":
    inputs = {
        "company_name": input("Company Name?\n"),
        "csv_file": input("Upload Excel file path:\n")
    }

    # Ensure the file exists
    if not os.path.isfile(inputs['csv_file']):
        print(f"Error: The file {inputs['csv_file']} does not exist.")
        exit(1)

    # Preprocess the data
    df, data_summary = preprocess_financial_data(inputs['csv_file'])

    # Include the data summary in inputs for agents to use
    inputs['data_summary'] = data_summary

    # Convert data_summary to a JSON-formatted string and escape curly braces
    data_summary_str = json.dumps(data_summary, indent=4)
    escaped_data_summary = escape_curly_braces(data_summary_str)

    # Now define the report_generation_agent, since we need inputs['company_name']
    report_generation_agent = Agent(
        role='Report Generation Agent',
        goal='Compile findings into comprehensive and precise reports for stakeholders, summarizing credit assessments',
        backstory=f"""You specialize in transforming analytical findings into clear, detailed reports.
Your reports facilitate informed decision-making for stakeholders.
You ensure that the reports accurately reflect the data interpretations and calculations based on the specified dataset structure and key terms.
The final report should include the following sections:

1. **Overview**:
    - Mention the name of the company ({inputs['company_name']}) and briefly describe what sections the report contains for reader reference.

2. **Financial Analysis on Key Metrics**:
    - Present the numbers and their brief descriptions together as bullet points first.
    - Then provide any comments on the financial data.
    - Make the information readable and easy to understand.

3. **Conclusions and Commentary: SWOT Analysis**:
    - Focus on what qualifies or disqualifies this business as credit-worthy.
    - Use financial information to support your points.
    - Emphasize aspects related to creditworthiness.

4. **Overall Assessment on Creditworthiness**:
    - Summarize the findings in an easy-to-read manner.
    - Keep the final creditworthiness score on a separate line towards the end.

Ensure that the report is well-structured, clear, and follows the specified formatting.""",
        verbose=True,
        allow_delegation=False
    )

    # Now define the tasks, including the escaped data summary

    task1 = Task(
        description=f"""Confirm receipt of the data and initiate the credit assessment process.
Ensure that the team is fully aware of the key terms and dataset structure provided, and emphasize the importance of interpreting the data exactly as specified.

{key_terms_and_structure}

Provide confirmation of data receipt and process initiation.""",
        expected_output="Confirmation of data receipt and process initiation, with acknowledgment of data interpretation guidelines",
        agent=credit_decision_manager
    )

    task2 = Task(
        description=f"""Analyze the preprocessed financial data provided in 'data_summary' to prepare signals and insights for determining creditworthiness.

Data Summary:
{escaped_data_summary}

Ensure that you interpret the data exactly as specified, correctly apply the column relations in your analysis, and prepare signals and insights for determining creditworthiness.

Focus on identifying key financial metrics relevant to creditworthiness, and provide commentary where necessary.

Be as deterministic as possible in your analysis.""",
        expected_output="Analyzed data with relevant features and insights extracted, including commentary on key metrics",
        agent=data_ingestion_analyst
    )

    task3 = Task(
        description=f"""Using the analyzed data from the Data Ingestion and Analyst Agent, evaluate the creditworthiness of the entity.

Use precise financial metrics and credit scoring models. Ensure that your assessment accurately reflects the data's implications on credit risk.

Prepare the following:
1. An overall assessment on creditworthiness with a score out of 10.
2. Conclusions and commentary over the financial data presented as a SWOT analysis (Strengths, Weaknesses, Opportunities, Threats).

Focus the SWOT analysis on what qualifies or disqualifies this business as credit-worthy, emphasizing aspects related to creditworthiness.

Incorporate the specific data provided, ensuring that your assessment is accurate.""",
        expected_output="Detailed credit risk assessment report, including a SWOT analysis focused on creditworthiness and a creditworthiness score out of 10",
        agent=credit_risk_assessment
    )

    task4 = Task(
        description=f"""Review the outputs from the Data Ingestion and Analyst Agent and the Credit Risk Assessment Agent.

Verify that all calculations and analyses are 100% accurate and reliable. Ensure that the data interpretations and calculations adhere exactly to the specified dataset structure and key terms.

Provide deterministic validation of all computations.

Confirm that the SWOT analysis and creditworthiness score are justified based on the data.

Ensure that the final report will meet the formatting and content requirements specified.""",
        expected_output="Validation report confirming accuracy or identifying issues, with specific references to data interpretations and assessments",
        agent=qa_agent
    )

    task5 = Task(
        description=f"""Compile the validated findings into a comprehensive and precise report for stakeholders, summarizing the credit assessment.

The final report should include the following sections:

1. **Overview**:
    - Mention the name of the company ({inputs['company_name']}) and briefly describe what sections the report contains for reader reference.

2. **Financial Analysis on Key Metrics**:
    - Present the numbers and their brief descriptions together as bullet points first.
    - Then provide any comments on the financial data.
    - Make the information readable and easy to understand.

3. **Conclusions and Commentary: SWOT Analysis**:
    - Focus on what qualifies or disqualifies this business as credit-worthy.
    - Use financial information to support your points.
    - Emphasize aspects related to creditworthiness.

4. **Overall Assessment on Creditworthiness**:
    - Summarize the findings in an easy-to-read manner.
    - Keep the final creditworthiness score on a separate line towards the end.

Ensure that the report is well-structured, clear, and follows the specified formatting.

Be as deterministic as possible in presenting the findings.""",
        expected_output="Final credit assessment report ready for stakeholders, including all specified sections",
        agent=report_generation_agent
    )

    # Instantiate your crew with a sequential process
    crew = Crew(
        agents=[
            credit_decision_manager,
            data_ingestion_analyst,
            credit_risk_assessment,
            qa_agent,
            report_generation_agent
        ],
        tasks=[task1, task2, task3, task4, task5],
        verbose=True,
        process=Process.sequential
    )

    # Get your crew to work!
    result = crew.kickoff(inputs=inputs)

    print("######################")
    print(result)
