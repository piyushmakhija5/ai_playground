import os
from dotenv import load_dotenv
from crewai import Agent, Task, Crew, Process
import pandas as pd
import numpy as np
import json
import streamlit as st
import time
import threading

load_dotenv()

# Define the agents with updated backstories to reflect monetary units in INR

credit_decision_manager = Agent(
    role='Credit Decision Manager',
    goal='Oversee the credit assessment process and interface with customers',
    backstory="""You are the customer-facing representative and orchestrator of the credit underwriting team.
You ensure that client needs are met and coordinate the workflow among the team members.
You have a deep understanding of the key terms and dataset structure provided, and you make sure the team interprets the data exactly as specified.
All monetary values are in Indian Rupees (INR).""",
    verbose=False,
    allow_delegation=True
)

data_ingestion_analyst = Agent(
    role='Data Ingestion and Analyst Agent',
    goal='Analyze preprocessed financial data to prepare signals for creditworthiness determination',
    backstory="""You specialize in handling financial data that has been preprocessed.
You interpret the provided data exactly as specified and extract relevant features and insights for credit assessment.
All monetary values are in Indian Rupees (INR).""",
    verbose=False,
    allow_delegation=False
)

credit_risk_assessment = Agent(
    role='Credit Risk Assessment Agent',
    goal='Evaluate the creditworthiness of entities using precise financial metrics',
    backstory="""You are an expert in financial analysis and risk modeling.
You use the provided metrics to assess credit risk accurately.
Based on the available data, you will adjust the existing credit score by +/- 20 points, focusing on what qualifies or disqualifies this business as credit-worthy.
All monetary values are in Indian Rupees (INR).""",
    verbose=False,
    allow_delegation=False
)

qa_agent = Agent(
    role='Quality Assurance Agent',
    goal='Ensure all calculations and analyses are 100% accurate and reliable',
    backstory="""You meticulously review outputs from other agents.
Your attention to detail ensures that all findings are precise before they are finalized.
You verify that the data interpretations and calculations adhere exactly to the specified dataset structure and key terms.
Confirm that the final report meets the formatting and content requirements.
Ensure that only information derived from the 'data_summary' is included in the updated credit report.
All monetary values are in Indian Rupees (INR).""",
    verbose=False,
    allow_delegation=False
)

# Function to escape curly braces in strings
def escape_curly_braces(s):
    return s.replace('{', '{{').replace('}', '}}')

# Function to convert NumPy and pandas types to native Python types
def convert_numpy_types(obj):
    if isinstance(obj, dict):
        return {convert_numpy_types(k): convert_numpy_types(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_numpy_types(v) for v in obj]
    elif isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, pd.Period):
        return str(obj)
    elif pd.isna(obj):
        return None
    else:
        return obj

# Updated preprocess_financial_data function with additional metrics
def preprocess_financial_data(file):
    import pandas as pd
    import numpy as np

    # Load the data
    df = pd.read_csv(file)

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

    # Ensure date columns are in datetime format with specified date format
    if 'Order Date' in df.columns:
        df['Order Date'] = pd.to_datetime(df['Order Date'], format='%d/%m/%Y', errors='coerce')
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

    # Existing Metrics

    # Total number of orders
    total_orders = len(df)

    # Total Net Sales
    total_net_sales = df['Net Sales Excl Gst'].sum()

    # Average Order Value (AOV)
    average_order_value = total_net_sales / total_orders if total_orders > 0 else 0

    # Discount as a percentage of Net Sales Excl Gst
    total_discount = df['Total Discount'].sum()
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

    # Return rate (Return Percentage/Return Ratio)
    if 'Order Status' in df.columns:
        total_returns = df[df['Order Status'].str.lower().isin(['returned', 'free_replacement'])].shape[0]
        return_rate = (total_returns / total_orders * 100) if total_orders > 0 else 0
    else:
        total_returns = 0
        return_rate = 0

    # Cost of return as a percentage of sales
    total_return_charges = df['Returned Charges Excl Gst'].sum()
    cost_of_return_percentage = (total_return_charges / total_net_sales * 100) if total_net_sales > 0 else 0

    # Logistics cost as a percentage of sales
    total_delivered_charges = df['Delivered Charges Excl Gst'].sum()
    logistics_cost_percentage = (total_delivered_charges / total_net_sales * 100) if total_net_sales > 0 else 0

    # SKU-wise sales
    if 'SKU ID' in df.columns:
        sku_sales = df.groupby('SKU ID')['Net Sales Excl Gst'].sum()
        # SKUs contributing to 80% of sales
        sku_sales_sorted = sku_sales.sort_values(ascending=False)
        cumulative_sales = sku_sales_sorted.cumsum()
        total_sales = sku_sales_sorted.sum()
        skus_contributing_80_percent_sales = cumulative_sales[cumulative_sales <= 0.8 * total_sales].count()
    else:
        skus_contributing_80_percent_sales = 0

    # Active days (business transaction period)
    min_order_date = df['Order Date'].min()
    max_order_date = df['Order Date'].max()
    days_active = (max_order_date - min_order_date).days + 1 if pd.notnull(min_order_date) and pd.notnull(max_order_date) else 0

    # Total categories
    total_categories = df['Product Category'].nunique() if 'Product Category' in df.columns else 0

    # Order and Net Sales Growth over Weeks/Months
    if 'Order Date' in df.columns and df['Order Date'].notnull().any():
        df['Order Month'] = df['Order Date'].dt.to_period('M')
        orders_per_month = df.groupby('Order Month').size()
        net_sales_per_month = df.groupby('Order Month')['Net Sales Excl Gst'].sum()

        # Convert Period index to string
        orders_per_month.index = orders_per_month.index.astype(str)
        net_sales_per_month.index = net_sales_per_month.index.astype(str)

        # Calculate month-over-month growth rates
        order_growth = orders_per_month.pct_change().fillna(0) * 100
        net_sales_growth = net_sales_per_month.pct_change().fillna(0) * 100

        # Average growth rates
        average_order_growth = order_growth.mean()
        average_net_sales_growth = net_sales_growth.mean()

        # Additional return metrics over time
        returns_per_month = df[df['Order Status'].str.lower().isin(['returned', 'free_replacement'])].groupby('Order Month').size()
        returns_per_month.index = returns_per_month.index.astype(str)
        return_rate_per_month = (returns_per_month / orders_per_month * 100).fillna(0)
    else:
        average_order_growth = 0
        average_net_sales_growth = 0
        orders_per_month = pd.Series(dtype='float64')
        net_sales_per_month = pd.Series(dtype='float64')
        order_growth = pd.Series(dtype='float64')
        net_sales_growth = pd.Series(dtype='float64')
        return_rate_per_month = pd.Series(dtype='float64')

    # Additional Metrics based on available data

    # Cost of Doing Business Percentage
    total_charges_fee = df['Total Charges/Fee'].sum()
    codb_percentage = (total_charges_fee / total_net_sales * 100) if total_net_sales > 0 else 0

    # Total Tax Liability Percentage
    total_tax_liability = df['Total Tax liability'].sum()
    total_tax_liability_percentage = (total_tax_liability / total_net_sales * 100) if total_net_sales > 0 else 0

    # TCS Sum and TCS Percentage
    total_tcs = df['TCS'].sum()
    tcs_percentage = (total_tcs / total_net_sales * 100) if total_net_sales > 0 else 0

    # TDS Sum and TDS Percentage
    total_tds = df['TDS'].sum()
    tds_percentage = (total_tds / total_net_sales * 100) if total_net_sales > 0 else 0

    # Profit Margin Percentage
    net_revenue = df['Net Revenue Excl Gst'].sum()
    profit_margin_percentage = (net_revenue / total_net_sales * 100) if total_net_sales > 0 else 0

    # Delivery Rate
    if 'Order Status' in df.columns:
        total_delivered = df[df['Order Status'].str.lower() == 'delivered'].shape[0]
        delivery_rate = (total_delivered / total_orders * 100) if total_orders > 0 else 0
    else:
        delivery_rate = 0

    # Assemble the summary
    summary = {
        'Total Discount Sum (INR)': total_discount,
        'Total Tax Liability Sum (INR)': total_tax_liability,
        'Total Charges/Fee Sum (INR)': total_charges_fee,
        'Average Biggest Charge/Fee (INR)': df['Biggest Charge/Fee'].mean(),
        'Total Net Sales Excl Gst (INR)': total_net_sales,
        'Total Net Revenue Excl Gst (INR)': net_revenue,
        'Total Listing Gmv (INR)': df['Listing Gmv'].sum(),
        'Total Orders': total_orders,
        'Average Order Value (INR)': average_order_value,
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
        'Average Monthly Order Growth (%)': average_order_growth,
        'Average Monthly Net Sales Growth (%)': average_net_sales_growth,
        'Orders Per Month': orders_per_month.to_dict(),
        'Net Sales Per Month (INR)': net_sales_per_month.to_dict(),
        'Order Growth Rate Per Month (%)': order_growth.to_dict(),
        'Net Sales Growth Rate Per Month (%)': net_sales_growth.to_dict(),
        'Return Rate Per Month (%)': return_rate_per_month.to_dict(),
        'Cost of Doing Business Percentage': codb_percentage,
        'Total Tax Liability Percentage': total_tax_liability_percentage,
        'TCS Sum (INR)': total_tcs,
        'TCS Percentage': tcs_percentage,
        'TDS Sum (INR)': total_tds,
        'TDS Percentage': tds_percentage,
        'Profit Margin Percentage': profit_margin_percentage,
        'Delivery Rate': delivery_rate,
        # Add more summary metrics as needed
    }

    return df, summary

# # Function to display the before credit report
# def load_before_report(company_name):
#     # Map company names to report filenames
#     company_reports = {
#         'Good Corp Pvt. Ltd.': 'Good_Corp_Credit_Report.md',
#         'Average Corp Pvt. Ltd.': 'Average_Corp_Credit_Report.md',
#         'Bad Corp Pvt. Ltd.': 'Bad_Corp_Credit_Report.md'
#     }

#     report_file = company_reports.get(company_name, None)

#     if report_file and os.path.exists(report_file):
#         with open(report_file, 'r') as f:
#             before_report = f.read()
#             st.markdown(before_report)
#             return before_report
#     else:
#         st.warning("No matching credit report found for the given company name.")
#         return None

def load_base_report(company_name):
    # Map company names to filenames
    company_to_filename = {
        'Good Corp': 'Good_Corp_Credit_Report.md',
        'Average Corp': 'Average_Corp_Credit_Report.md',
        'Bad Corp': 'Bad_Corp_Credit_Report.md',
    }
    filename = company_to_filename.get(company_name)
    if filename:
        try:
            with open(f'reports/{filename}', 'r') as file:
                report = file.read()
            return report
        except FileNotFoundError:
            st.error(f'Base report file {filename} not found.')
            return None
    else:
        st.error('No base report found for the provided company name.')
        return None

# Streamlit App
def main():
    # Create two columns for the logo and the title
    col1, col2 = st.columns([1, 4])

    with col1:
        st.image('assets/moneyflo_logo.png', width=100)

    with col2:
        st.title("Credit Risk Assessment")

    st.write("Please provide the company details and upload the financial data.")

    # Input fields
    company_name = st.text_input("Company Name")
    uploaded_file = st.file_uploader("Upload CSV file", type=["csv"])

    if company_name and uploaded_file:
        # Load the base report
        before_report = load_base_report(company_name)
        if before_report is None:
            st.stop()  # Stop execution if base report is not found
        # Display the before report
        st.markdown('## Original Credit Report')
        st.markdown(before_report)

        # Preprocess the data
        df, data_summary = preprocess_financial_data(uploaded_file)

        # Convert data types
        data_summary_converted = convert_numpy_types(data_summary)

        # Include the data summary in inputs for agents to use
        inputs = {
            "company_name": company_name,
            "data_summary": data_summary_converted,
            "before_report": before_report
        }

        # Convert data_summary to a JSON-formatted string and escape curly braces
        data_summary_str = json.dumps(data_summary_converted, indent=4)
        escaped_data_summary = escape_curly_braces(data_summary_str)

        # Now define the report_generation_agent with updated backstory
        report_generation_agent = Agent(
            role='Report Generation Agent',
            goal='Compile findings into comprehensive and precise reports for stakeholders, summarizing credit assessments',
            backstory=f"""You specialize in transforming analytical findings into clear, detailed reports.
Your reports facilitate informed decision-making for stakeholders.
You ensure that the reports accurately reflect the data interpretations and calculations based on the specified dataset structure and key terms.
All monetary values are in Indian Rupees (INR).

When updating the credit report, only include information that can be derived from the 'data_summary' provided.
Do not include any information that is not present in the 'data_summary'.

Adjust the credit score by modifying it by +/- 20 points based on the analysis of the alternative data.

Ensure that the report uses the same credit scale and format as the original credit report.

In the financial summary section, include detailed numbers, preferably in tabular form, using the alternative data. Make sure these numbers are 100% accurate.

In the summary section, only provide strong positive or negative information, or things that need to be monitored.

Highlight recommendations for negative signals.

Ensure that the summary section starts with the same format as the original report and includes the credit score.

Be as deterministic as possible in presenting the findings.""",
            verbose=False,
            allow_delegation=False
        )

        # Now define the tasks, including the escaped data summary
        task1 = Task(
            description=f"""Confirm receipt of the data and initiate the credit assessment process.
Ensure that the team is fully aware of the key terms and dataset structure provided, and emphasize the importance of interpreting the data exactly as specified.
All monetary values are in Indian Rupees (INR).

Provide confirmation of data receipt and process initiation.""",
            expected_output="Confirmation of data receipt and process initiation, with acknowledgment of data interpretation guidelines",
            agent=credit_decision_manager
        )

        task2 = Task(
            description=f"""Analyze the preprocessed financial data provided in 'data_summary' to calculate relevant metrics and prepare signals for determining creditworthiness.

Data Summary:
{escaped_data_summary}

Ensure that you interpret the data exactly as specified, correctly apply the column relations in your analysis, and prepare signals and insights for determining creditworthiness.
All monetary values are in Indian Rupees (INR).

Be as deterministic as possible in your analysis.""",
            expected_output="Analyzed data with relevant metrics calculated and insights extracted",
            agent=data_ingestion_analyst
        )

        task3 = Task(
            description=f"""Using the analyzed data from the Data Ingestion and Analyst Agent, evaluate the creditworthiness of the entity.

Use precise financial metrics to assess credit risk accurately.

All monetary values are in Indian Rupees (INR).

Based on the analysis of the alternative data ('data_summary'), prepare the following:

1. Adjust the existing credit score from the before report by modifying it by +/- 20 points based on the alternative data.
2. Conclusions and commentary based on the available data, focusing on what qualifies or disqualifies this business as credit-worthy.

Incorporate the specific data provided in 'data_summary', ensuring that your assessment is accurate.

Only use information derived from 'data_summary' for your evaluation.

Do not include any information that is not provided in 'data_summary'.""",
            expected_output="Detailed credit risk assessment report with conclusions and an adjusted credit score, modifying the existing score by +/- 20 points based on the analysis.",
            agent=credit_risk_assessment
        )

        task4 = Task(
            description=f"""Review the outputs from the Data Ingestion and Analyst Agent and the Credit Risk Assessment Agent.

Verify that all calculations and analyses are 100% accurate and reliable.

Ensure that the data interpretations and calculations adhere exactly to the specified dataset structure and key terms.

Ensure that only information derived from 'data_summary' is included in the updated credit report.

Confirm that no unnecessary or extraneous information is being passed to the updated credit report.

Check that the financial summary section includes detailed numbers, preferably in tabular form, using the alternative data, and that these numbers are 100% accurate.

Ensure that the summary section only provides strong positive or negative information, or things that need to be monitored.

Confirm that recommendations are highlighted for negative signals.

Ensure that the summary section starts with the same format as the original report and includes the credit score.

All monetary values are in Indian Rupees (INR).

Provide deterministic validation of all computations.

Confirm that the conclusions and adjusted credit score are justified based on the data.

Ensure that the final report will meet the formatting and content requirements specified.""",
            expected_output="Validation report confirming accuracy or identifying issues, with specific references to data interpretations and assessments. Ensure no unnecessary information is included, and that the report meets all specified requirements.",
            agent=qa_agent
        )

        task5 = Task(
            description=f"""Compile the validated findings into an updated credit report for stakeholders, incorporating the alternative data provided.

The final report should be based on the following before version of the credit report:

Before Credit Report:
{inputs['before_report']}

Update the report by including the alternative data from 'data_summary' and highlight the sections impacted by this data.

Ensure that the updated report includes the following:

- Use the same credit scale and format as the original credit report.
- Adjust the credit score by modifying it by +/- 20 points based on the analysis of the alternative data.
- In the financial summary section, include detailed numbers, preferably in tabular form, using the alternative data. Make sure these numbers are 100% accurate.
- In the summary section, only provide strong positive or negative information, or things that need to be monitored.
- Highlight recommendations for negative signals.
- Ensure that the summary section starts with the same format as the original report and includes the credit score.
- Only add information that can be derived from the 'data_summary'.
- Do not include any information that is not provided in the 'data_summary'.

Highlight the sections that have been updated or impacted by the alternative data. Use bold text or color coding (e.g., <span style="color:red">updated text</span>) to indicate changes.

Ensure that the report is well-structured, clear, and follows the specified formatting.

All monetary values are in Indian Rupees (INR).

Be as deterministic as possible in presenting the findings.""",
            expected_output="Updated credit report with sections impacted by alternative data highlighted, including a detailed financial summary with accurate numbers, and an appropriate summary section as per the requirements.",
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

        # Display a separator
        st.markdown('---')

        # Display a loader message with time elapsed
        status_text = st.empty()
        start_time = time.time()
        processing_complete = False
        result = None

        # Function to run crew.kickoff()
        def run_crew():
            nonlocal result
            result = crew.kickoff(inputs=inputs)
            nonlocal processing_complete
            processing_complete = True

        # Start the crew.kickoff() in a separate thread
        processing_thread = threading.Thread(target=run_crew)
        processing_thread.start()

        # Update the status message with time elapsed
        while not processing_complete:
            elapsed_time = int(time.time() - start_time)
            status_text.text(f"Processing... Time elapsed: {elapsed_time} seconds")
            time.sleep(1)

        # After processing is complete
        total_time = int(time.time() - start_time)
        status_text.text(f"Processing complete. Total time: {total_time} seconds")

        # Display the after report
        st.markdown('## Updated Credit Report')
        st.markdown(result, unsafe_allow_html=True)
    else:
        st.warning("Please provide both the company name and upload the CSV file.")

if __name__ == "__main__":
    main()