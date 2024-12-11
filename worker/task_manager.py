from celery import Celery
from agents.crews.content_creation.crew import ContentCreation
from agents.crews.financial_analysis.crew import FinancialAnalysis

celery = Celery("tasks", broker="redis://localhost:6379/0")

@celery.task
def execute_agent(agent_name: str, inputs: dict):
    """
    Execute the given agent asynchronously.
    """
    agent_map = {
        "content_creation": ContentCreation,
        "financial_analysis": FinancialAnalysis,
        # Add more agents here
    }

    if agent_name not in agent_map:
        raise ValueError(f"Agent '{agent_name}' not found.")
    
    agent_class = agent_map[agent_name]()
    return agent_class.crew().kickoff(inputs=inputs)
