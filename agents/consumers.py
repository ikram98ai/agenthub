from channels.generic.websocket import AsyncWebsocketConsumer
import json
from channels.db import database_sync_to_async

class AgentTaskConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.agent_id = self.scope['url_route']['kwargs']['agent_id']
        self.room_group_name = f'agent_{self.agent_id}'

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        # Handle any messages from client if needed
        pass

    async def task_update(self, event):
        # Send task update to WebSocket
        await self.send(text_data=json.dumps(event['data']))

    @database_sync_to_async
    def get_response_data(self, response_id):
        from .models import AgentResponse
        response = AgentResponse.objects.get(id=response_id)
        return {
            'output': response.get_html_content(),
            'execution_time': response.execution_time(),
            'status': response.status
        }


