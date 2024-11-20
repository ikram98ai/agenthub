from django.db import models
from django.contrib.auth.models import User  # For user authentication


class Usecase(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name
    
class AgentLLM(models.Model):
    name = models.CharField(max_length=100)
    
    def __str__(self):
        return self.name

class Agent(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    url = models.URLField(default="#")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='agents')
    usecases = models.ManyToManyField(Usecase, related_name='agents')
    llms =  models.ManyToManyField(AgentLLM, related_name='agents')
    def __str__(self):
        return self.name
    

class AgentInput(models.Model):
    name = models.CharField(max_length=100)
    agent = models.ForeignKey(Agent,on_delete=models.CASCADE,related_name='inputs')

    def __str__(self):
        return self.name

class Chat(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chats')
    agent = models.ForeignKey(Agent, on_delete=models.CASCADE, related_name='chats')
    started_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Chat with {self.agent.name} by {self.user.username}"

class ChatMessage(models.Model):
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, related_name='messages')
    sender = models.CharField(max_length=10, choices=[('user', 'User'), ('agent', 'Agent')])
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sender} - {self.message[:30]}"

class Process(models.Model):
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, related_name='processes')
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
