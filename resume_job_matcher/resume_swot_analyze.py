# Import dependencies
import os
from crewai import Crew, Process
from dotenv import load_dotenv, find_dotenv  # Groq, SerpApi
from langchain_groq import ChatGroq  # Mixtral, Gemma, Llama2
from utils import *
from agents import agents
from tasks import tasks

load_dotenv(find_dotenv())

# Load Config
os.environ["SERPER_API_KEY"] = os.getenv("SERPER_API_KEY")
os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY")

## Initialize LLM
llm = ChatGroq(model="gemma-7b-it", temperature=0)

# Input data
resume = read_all_pdf_pages("data/resume.pdf")
job_desire = input("Enter Desiring Job: ")

# Create agents and tasks
job_requirements_researcher, resume_swot_analyzer = agents(llm)
research, swot_analysis = tasks(llm, job_desire, resume)

# build crew
crew = Crew(
    agents=[job_requirements_researcher, resume_swot_analyzer],
    tasks=[research, swot_analysis],
    verbose=1,
    process=Process.sequential,
)

# Kickoff crew
result = crew.kickoff()
print(result)
