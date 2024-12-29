# tasks.py
from celery import shared_task
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.utils import timezone
from .crews.content_creation.crew import ContentCreation
from .crews.event_planning.crew import EventPlanning
from .crews.customer_outreach.crew import CustomerOutreach
from .crews.financial_analysis.crew import FinancialAnalysis
from .crews.research_write_article.crew import ArticleResearchWriter
from .models import AgentResponse

@shared_task(bind=True)
def execute_agent(self, agent_name: str, inputs: dict, response_id=None):
    """
    Execute the agent and send real-time updates through WebSocket
    """
    channel_layer = get_channel_layer()
    
    try:
        # Get the response object
        response = AgentResponse.objects.get(id=response_id)
        agent_id = response.agent.id
        
        # Send initial status
        async_to_sync(channel_layer.group_send)(
            f'agent_{agent_id}',
            {
                'type': 'task_update',
                'data': {
                    'status': 'processing',
                    'message': 'Task started processing',
                    'response_id': response_id,
                    'task_id': self.request.id
                }
            }
        )

        # Your existing agent execution logic
        agent_map = {
            "Content creation": ContentCreation,
            "Financial analysis": FinancialAnalysis,
            "Customer outreach": CustomerOutreach,
            "Event planning": EventPlanning,
            "Research write article": ArticleResearchWriter
        }

        if agent_name not in agent_map:
            raise ValueError(f"Agent '{agent_name}' not found.")

        agent_class = agent_map[agent_name]()
        result = agent_class.crew().kickoff(inputs=inputs)

        # Update response in database
        response.output = str(result)
        response.completed_at = timezone.now()
        response.status = 'completed'
        response.save()

        # Send completion status
        async_to_sync(channel_layer.group_send)(
            f'agent_{agent_id}',
            {
                'type': 'task_update',
                'data': {
                    'status': 'completed',
                    'output': response.get_html_content(),
                    'execution_time': response.execution_time(),
                    'response_id': response_id
                }
            }
        )

        return result

    except Exception as e:
        if response_id:
            try:
                response = AgentResponse.objects.get(id=response_id)
                response.status = 'failed'
                response.error_message = str(e)
                response.completed_at = timezone.now()
                response.save()

                # Send error status
                async_to_sync(channel_layer.group_send)(
                    f'agent_{response.agent.id}',
                    {
                        'type': 'task_update',
                        'data': {
                            'status': 'failed',
                            'error': str(e),
                            'response_id': response_id
                        }
                    }
                )
            except Exception as inner_e:
                print(f"Error updating response: {inner_e}")

        raise