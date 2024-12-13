from celery import shared_task
from .models import AgentResponse
from agents.crews.content_creation.crew import ContentCreation
from agents.crews.financial_analysis.crew import FinancialAnalysis

@shared_task
def execute_agent(agent_name: str, inputs: dict, response_id=None):
    """
    Execute the given agent asynchronously.
    """
    agent_map = {
        "content_creation": ContentCreation,
        "Financial analysis": FinancialAnalysis,
    }

    if agent_name not in agent_map:
        raise ValueError(f"Agent '{agent_name}' not found.")

    agent_class = agent_map[agent_name]()
    result = str(agent_class.crew().kickoff(inputs=inputs))

    # Update the AgentResponse with the result
    if response_id:
        try:
            agent_response = AgentResponse.objects.get(id=response_id)
            agent_response.output = result
            agent_response.save()
        except AgentResponse.DoesNotExist as e:
             # Update response with an error message
            response = AgentResponse.objects.get(pk=response_id)
            response.output = f"Error: {str(e)}"
            response.save()


    return result
