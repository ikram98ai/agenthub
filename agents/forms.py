from django import forms
from .models import AgentInput

class AgentInputForm(forms.Form):
    def __init__(self, *args, agent=None, **kwargs):
        super().__init__(*args, **kwargs)
        if agent:
            for agent_input in agent.inputs.all():
                field_type = forms.CharField
                if agent_input.input_type != 'text':
                    field_type = forms.FileField
                self.fields[f'input_{agent_input.id}'] = field_type(
                    label=agent_input.name,
                    required=agent_input.is_required,
                    help_text=agent_input.description
                )
                self.fields[f'input_{agent_input.id}'].widget.attrs['class'] = 'w-full bg-gray-200 appearance-none border-2 border-gray-200 rounded w-full py-2 px-4 text-gray-700 leading-tight focus:outline-none focus:bg-white focus:border-purple-500'
