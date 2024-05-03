# Agents
## 1. Job Requirements Researcher
## 2. Resume SWOT Analyzer

# Import dependencies
from crewai import Agent
from crewai_tools import SerperDevTool, WebsiteSearchTool

search_tool = SerperDevTool()
web_rag_tool = WebsiteSearchTool()


# Create Agents that use the above tools
def agents(llm):
    """Has 2 agents
    1. requirements researcher - search_tool, web_rag_tool
    2. SWOT analyzer
    """
    job_requirements_researcher = Agent(
        role="Market Research Analyzer",
        goal="Provide up-to-date market analysis of industry job requirements of the domain specified",
        backstory="An expert analyst with a keen eye for market trends",
        tools=[search_tool, web_rag_tool],
        verbose=True,
        llm=llm,
        max_iters=5,
    )
    resume_swot_analyzer = Agent(
        role="Resume SWOT analysis",
        goal="Perform a SWOT Analysis on the Resume based on the industry Job Requirements from job_requirements_researcher and provide a json report.",
        backstory="An exper in hiring so has a great idea on resumes",
        verbose=True,
        llm=llm,
        max_iters=5,
        allow_delegation=True,
    )

    return job_requirements_researcher, resume_swot_analyzer
