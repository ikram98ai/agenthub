from django.db import models
from django.contrib.auth import get_user_model


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
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=False)
    updated_at = models.DateTimeField(auto_now=True)
    uploaded_by = models.ForeignKey(get_user_model(), on_delete=models.SET_NULL, null=True, related_name='agents')
    usecases = models.ManyToManyField(Usecase, related_name='agents',blank=True)
    llms =  models.ManyToManyField(AgentLLM, related_name='agents',blank=True)
    def __str__(self):
        return self.name
    

    def get_absolute_url(self):
        return reverse('agent-detail', args=[str(self.id)])
    
    class Meta:
        indexes = [
            models.Index(fields=['name', 'is_active']),
            models.Index(fields=['-created_at'])
        ]


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

    class Meta:
        indexes = [
            models.Index(fields=['agent', 'input_type'])
        ]

class AgentResponse(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.SET_NULL,null=True, related_name='responses')
    agent = models.ForeignKey(Agent, on_delete=models.CASCADE, related_name='responses')
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(auto_now=True)
    output = models.TextField(blank=True, null=True)
    status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending'),
            ('processing', 'Processing'),
            ('completed', 'Completed'),
            ('failed', 'Failed')
        ],
        default='pending',
        db_index=True
    )
    error_message = models.TextField(null=True, blank=True)
    task_id = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        ordering = ['-started_at']
        indexes = [
            models.Index(fields=['user', '-started_at']),
            models.Index(fields=['agent', 'status'])
        ]

    def __str__(self):
        return f"{self.agent.name} - {self.user.username}"

    def execution_time(self):
        return (self.completed_at - self.started_at).seconds

    def get_html_content(self):
        from markdown2 import markdown
        return markdown(self.output) if self.output else None

class AgentResponseInput(models.Model):
    agent_response = models.ForeignKey(AgentResponse, on_delete=models.CASCADE, related_name='response_inputs')
    agent_input = models.ForeignKey(AgentInput, on_delete=models.CASCADE, related_name='response_inputs')
    value = models.TextField()  # Store the user's input here (text, file path, image URL, etc.)
    is_valid = models.BooleanField(default=True)  # Optional: To track if the input is valid (for required fields, etc.)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f" {self.agent_input.name}: {self.value}"
    
    class Meta:
        indexes = [
            models.Index(fields=['agent_response', 'agent_input']),
        ]
