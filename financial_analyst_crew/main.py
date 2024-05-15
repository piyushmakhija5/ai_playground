import os
from dotenv import load_dotenv

load_dotenv()

from crew import FinancialAnalystCrew


def run():
    inputs = input("Company Name?\n")
    FinancialAnalystCrew().crew().kickoff(inputs=inputs)


if __name__ == "__main__":
    run()
