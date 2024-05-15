from crewai import Agent
from crewai_tools.tools import WebsiteSearchTool, SerperDevTool, FileReadTool

web_search_tool = WebsiteSearchTool()
serper_dev_tool = SerperDevTool()
file_read_tool = FileReadTool(
    file_path="job_description_example.md",
    description="A tool to read the job description example file",
)


class Agents:
    def research_agent(self):
        return Agent(
            role="Research Aanalyst",
            goal="Analyze the ocmpany website and provide the description to extract insights on culture, values, and specific needs",
            tools=[web_search_tool, serper_dev_tool],
            backstory="Expert in analyzing company culture and identifying key values and needs from various sources, including websites and brief descriptions",
            verbose=True,
        )

    def writer_agent(self):
        return Agent(
            role="Job Description Writer",
            goal="Use the insights from the Research Analyst to create a detailed, engaging and enticing job posting",
            tools=[web_search_tool, serper_dev_tool, file_read_tool],
            backstory="Skilled in crafting compeling job descriptions that resonate with the company's values and attract the right candidates",
            verbose=True,
        )

    def review_agent(self):
        return Agent(
            role="Review and Editing Specialist",
            goal="Review the job posting for clarity, engagement, grammatical accuracy and alignment with the company values and refine it to ensure perfection.",
            tools=[web_search_tool, serper_dev_tool, file_read_tool],
            backstory="Skilled in crafting compelling job descriptions that resonate with the company's values and attract the right candidates.",
            verbose=True,
        )
