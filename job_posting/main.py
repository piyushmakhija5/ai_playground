import os
from crewai import Crew, Process
from dotenv import load_dotenv, find_dotenv  # Groq
from langchain_groq import ChatGroq  # Mixtral, Gemma, Llama2
from tasks import Tasks
from agents import Agents

tasks = Tasks()
agents = Agents()
load_dotenv(find_dotenv())

# Load Config
os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY")

## Initialize LLM
llm = ChatGroq(model="gemma-7b-it", temperature=0)

company_description = input("What is the company description?\n")
company_domain = input("What is the company domain?\n")
hiring_needs = input("What are the hiring needs?\n")
specific_benefits = input("What are the specific benefits you offer?\n")


# Create Agents
research_agent = agents.research_agent()
writer_agent = agents.writer_agent()
review_agent = agents.review_agent()

# Define Tasks for each agent
research_company_culture_task = tasks.research_company_culture_task(
    research_agent, company_description, company_domain
)
industry_analysis_task = tasks.industry_analysis_task(
    research_agent, company_domain, company_description
)
research_role_requirements_task = tasks.research_role_requirements_task(
    research_agent, hiring_needs
)
draft_job_posting_task = tasks.draft_job_posting_task(
    writer_agent, company_description, hiring_needs, specific_benefits
)
review_and_edit_job_posting_task = tasks.review_and_edit_job_posting_task(
    review_agent, hiring_needs
)

# Initiate crew with sequential process
crew = Crew(
    agents=[research_agent, writer_agent, review_agent],
    tasks=[
        research_company_culture_task,
        industry_analysis_task,
        research_role_requirements_task,
        draft_job_posting_task,
        review_and_edit_job_posting_task,
    ],
    verbose=2,
    process=Process.sequential,
)

## Kickoff the crew process
result = crew.kickoff()

print("Job Posting Creation Process Completed.")
print("Final Job Posting:")
print(result)
