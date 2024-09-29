import os
from dotenv import load_dotenv
from crewai import Agent, Task, Crew, Process
import numpy as np
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
- Biggest/Largest Charge/Fee: Charge or fee with the highest absolute value.
"""

# Function to preprocess and analyze the financial data

def preprocess_financial_data(csv_file_path):
    import pandas as pd

    # Load the data
    df = pd.read_excel(csv_file_path)

    # Ensure correct data types for numeric columns
    numeric_columns = [
        'Shipping Discount', 'Self Discount', 'Total Discount', 'Net Sales Excl Gst',
        'Delivered Charges Excl Gst', 'Returned Charges Excl Gst',
        'Free Replacement Charges Excl Gst', 'Indirect Charges Excl Gst',
        'Net Revenue Excl Gst', 'Output Gst', 'Input Credit Gst',
        'Listing Gmv', 'TCS', 'TDS'
    ]
    for col in numeric_columns:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
        else:
            df[col] = 0

    # Ensure date columns are in datetime format
    if 'Order Date' in df.columns:
        df['Order Date'] = pd.to_datetime(df['Order Date'], errors='coerce')
    else:
        df['Order Date'] = pd.NaT

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

    # Identify the Biggest/Largest Charge/Fee
    charges_cols = [
        'Delivered Charges Excl Gst',
        'Returned Charges Excl Gst',
        'Free Replacement Charges Excl Gst',
        'Indirect Charges Excl Gst'
    ]
    df['Biggest Charge/Fee'] = df[charges_cols].abs().max(axis=1)

    # Additional Metrics

    # Total number of orders
    total_orders = len(df)

    # Total Net Sales
    total_net_sales = df['Net Sales Excl Gst'].sum()

    # Average Order Value (AOV)
    average_order_value = total_net_sales / total_orders if total_orders > 0 else 0

    # Total Discount
    total_discount = df['Total Discount'].sum()

    # Discount as a percentage of Net Sales Excl Gst
    discount_percentage = (total_discount / total_net_sales * 100) if total_net_sales > 0 else 0

    # SKUs discount coverage: percentage of SKUs that had discounts
    if 'SKU ID' in df.columns:
        total_skus = df['SKU ID'].nunique()
        skus_with_discount = df[df['Total Discount'] > 0]['SKU ID'].nunique()
        skus_discount_coverage = (skus_with_discount / total_skus * 100) if total_skus > 0 else 0
    else:
        total_skus = 0
        skus_discount_coverage = 0

    # Self Discount and Shipping Discount ratio
    total_self_discount = df['Self Discount'].sum()
    total_shipping_discount = df['Shipping Discount'].sum()
    total_discounts = total_self_discount + total_shipping_discount
    self_discount_ratio = (total_self_discount / total_discounts * 100) if total_discounts > 0 else 0
    shipping_discount_ratio = (total_shipping_discount / total_discounts * 100) if total_discounts > 0 else 0

    # Return rate
    if 'Order Status' in df.columns:
        total_returns = df[df['Order Status'].str.lower().isin(['returned', 'free_replacement'])].shape[0]
        return_rate = (total_returns / total_orders * 100) if total_orders > 0 else 0
    else:
        return_rate = 0

    # Cost of return as a percentage of sales
    total_return_charges = df['Returned Charges Excl Gst'].sum()
    cost_of_return_percentage = (total_return_charges / total_net_sales * 100) if total_net_sales > 0 else 0

    # Logistics cost as a percentage of sales
    total_delivered_charges = df['Delivered Charges Excl Gst'].sum()
    logistics_cost_percentage = (total_delivered_charges / total_net_sales * 100) if total_net_sales > 0 else 0

    # SKU-wise sales
    sku_sales = df.groupby('SKU ID')['Net Sales Excl Gst'].sum()
    # SKUs contributing to 80% of sales
    sku_sales_sorted = sku_sales.sort_values(ascending=False)
    cumulative_sales = sku_sales_sorted.cumsum()
    total_sales = sku_sales_sorted.sum()
    skus_contributing_80_percent_sales = cumulative_sales[cumulative_sales <= 0.8 * total_sales].count()

    # Active days (business transaction period)
    min_order_date = df['Order Date'].min()
    max_order_date = df['Order Date'].max()
    days_active = (max_order_date - min_order_date).days + 1 if pd.notnull(min_order_date) and pd.notnull(max_order_date) else 0

    # Total categories
    total_categories = df['Product Category'].nunique() if 'Product Category' in df.columns else 0

    # Assemble the summary
    summary = {
        'Total Discount Sum': total_discount,
        'Total Tax Liability Sum': df['Total Tax liability'].sum(),
        'Total Charges/Fee Sum': df['Total Charges/Fee'].sum(),
        'Average Biggest Charge/Fee': df['Biggest Charge/Fee'].mean(),
        'Total Net Sales Excl Gst': total_net_sales,
        'Total Net Revenue Excl Gst': df['Net Revenue Excl Gst'].sum(),
        'Total Listing Gmv': df['Listing Gmv'].sum(),
        'Total Orders': total_orders,
        'Average Order Value': average_order_value,
        'Discount Percentage': discount_percentage,
        'SKUs Discount Coverage Percentage': skus_discount_coverage,
        'Self Discount Ratio': self_discount_ratio,
        'Shipping Discount Ratio': shipping_discount_ratio,
        'Return Rate': return_rate,
        'Cost of Return Percentage': cost_of_return_percentage,
        'Logistics Cost Percentage': logistics_cost_percentage,
        'SKUs Contributing 80% of Sales': skus_contributing_80_percent_sales,
        'Days Active': days_active,
        'Total SKUs': total_skus,
        'Total Categories': total_categories,
        # Add more summary metrics as needed
    }

    return df, summary

# Function to escape curly braces in strings
def escape_curly_braces(s):
    return s.replace('{', '{{').replace('}', '}}')

# Function to convert NumPy data types to native Python data types
def convert_numpy_types(obj):
    if isinstance(obj, dict):
        return {k: convert_numpy_types(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_numpy_types(v) for v in obj]
    elif isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    else:
        return obj

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

    # Convert NumPy data types to native Python types
    data_summary_converted = convert_numpy_types(data_summary)

    # Include the data summary in inputs for agents to use
    inputs['data_summary'] = data_summary_converted

    # Convert data_summary to a JSON-formatted string and escape curly braces
    data_summary_str = json.dumps(data_summary_converted, indent=4)
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
