from django import forms
from .models import AgentInput

class AgentInputForm(forms.Form):
    def __init__(self, *args, agent=None, **kwargs):
        super().__init__(*args, **kwargs)
        if agent:
            for agent_input in agent.inputs.all():
                field_type = forms.CharField
                if agent_input.input_type == 'file':
                    field_type = forms.FileField
                self.fields[f'input_{agent_input.id}'] = field_type(
                    label=agent_input.name,
                    required=agent_input.is_required,
                    help_text=agent_input.description
                )
