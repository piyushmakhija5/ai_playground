# Tasks
## 1. Find the Job Requirements
## 2. Resume Swot Analysis

from crewai import Task
from agents import agents


def tasks(llm, job_desire, resume_content):
    """
    research - Find the relevant skills, projects and experience
    swot_analysis - understand the report and the resume. Based on this make a swot analysis
    """
    job_requirements_researcher, resume_swot_analyzer = agents(llm)

    research = Task(
        description=f'For the Job position of Desire: {job_desire} research and identify the current market requirements for a person at the job including the relevant skills, some unique research projects or common projects along with what experience would be required. For searching query use ACTION INPUT KEY as "search_query"',
        expected_output="A report on what are the skills, projects and experience required and some unique real time projects that can be there which enhance the chance of a person to get a job.",
        agent=job_requirements_researcher,
    )

    swot_analysis = Task(
        description=f"Resume Content: {resume_content} \n Analyze the resume provided and the report of job_requirements_researcher to provide a detailed SWOT analysis report on the resume along with the Resume Match Percentage and Suggestions to improve",
        expected_output='A JSON formettted report as follows: "Candidate: candidate, "Strengths": [strengths], "Weaknesses": [weaknesses], "Oppurtunities": [opputtinities], "Threats":[threats], "Resume Match %": resume_match_percentage, "Suggestions":suggestions',
        agent=resume_swot_analyzer,
        output_file="reports/resume_review.json",
    )

    return research, swot_analysis
