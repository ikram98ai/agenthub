from django.db import models
from django.contrib.auth.models import User  # For user authentication


# models.py
from django.db import models
from django.urls import reverse


class Usecase(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

    
class AgentLLM(models.Model):
    name = models.CharField(max_length=100)
    
    def __str__(self):
        return self.name
    
class Agent(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    url = models.URLField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=False)
    updated_at = models.DateTimeField(auto_now=True)
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='agents')
    usecases = models.ManyToManyField(Usecase, related_name='agents')
    llms =  models.ManyToManyField(AgentLLM, related_name='agents')
    def __str__(self):
        return self.name
    

    def get_absolute_url(self):
        return reverse('agent-detail', args=[str(self.id)])


class AgentInput(models.Model):
    agent = models.ForeignKey(Agent, on_delete=models.CASCADE, related_name='inputs')
    name = models.CharField(max_length=100)
    input_type = models.CharField(max_length=50, choices=[
        ('text', 'Text'),
        ('file', 'File'),
        ('image', 'Image'),
        ('video', 'Video'),
        ('audio', 'Audio'),
    ],default='text')
    is_required = models.BooleanField(default=True)
    description = models.TextField(blank=True, null=True)    
    def __str__(self):
        return f"{self.agent.name} - {self.name}"


class AgentResponse(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chats')
    agent = models.ForeignKey(Agent, on_delete=models.CASCADE, related_name='chats')
    started_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.agent.name} - {self.user.username}"


class AgentResponseInput(models.Model):
    agent_response = models.ForeignKey(AgentResponse, on_delete=models.CASCADE, related_name='response_inputs')
    agent_input = models.ForeignKey(AgentInput, on_delete=models.CASCADE, related_name='response_inputs')
    value = models.TextField()  # Store the user's input here (text, file path, image URL, etc.)
    is_valid = models.BooleanField(default=True)  # Optional: To track if the input is valid (for required fields, etc.)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.agent_response.user.username} - {self.agent_input.name}: {self.value}"

class Process(models.Model):
    response = models.ForeignKey(AgentResponse, on_delete=models.CASCADE, related_name='processes')
    agent = models.ForeignKey(Agent, on_delete=models.CASCADE, related_name='processes')
    name = models.CharField(max_length=100)
    status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('failed', 'Failed')
    ], default='pending')
    output = models.TextField(null=True, blank=True)
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Process {self.name} for {self.agent.name} ({self.status})"


# class Chat(models.Model):
#     user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chats')
#     agent = models.ForeignKey(Agent, on_delete=models.CASCADE, related_name='chats')
#     started_at = models.DateTimeField(auto_now_add=True)
#     ended_at = models.DateTimeField(null=True, blank=True)

#     def __str__(self):
#         return f"Chat with {self.agent.name} by {self.user.username}"

# class ChatMessage(models.Model):
#     chat = models.ForeignKey(Chat, on_delete=models.CASCADE, related_name='messages')
#     sender = models.CharField(max_length=10, choices=[('user', 'User'), ('agent', 'Agent')])
#     message = models.TextField()
#     timestamp = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return f"{self.sender} - {self.message[:30]}"