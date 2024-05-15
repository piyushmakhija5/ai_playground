from crewai import Agent, Crew, Process, Task
from crewai.project import CrewaBase, agent, crew, Task
from langchain_groq import ChatGroq


@CrewBase
class FinancialAnalystCrew:
    """Financial Analyst Crew"""

    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

    def __init__(self) -> None:
        self.groq_llm = ChatGroq(temperature=0, model_name="mixtral-8x7b-32768")

    @agent
    def company_researcher(self) -> Agent:
        return Agent(config=self.agents_config["company_researcher"], llm=self.groq_llm)

    @agent
    def company_analyst(self) -> Agent:
        return Agent(config=self.agents_config["company_analyst"], llm=self.groq_llm)

    @task
    def research_company_task(self) -> Task:
        return Task(
            config=self.tasks_config["research_company_task"],
            agent=self.company_researcher,
        )

    @task
    def analyze_company_task(self) -> Task:
        return Task(
            config=self.tasks_config["analyze_company_task"], agent=self.company_analyst
        )
