from django.contrib import admin
from .models import Usecase,AgentLLM, Agent, AgentInput, Process, AgentResponse, AgentResponseInput
from django import forms


@admin.register(Usecase)
class UsecaseAdmin(admin.ModelAdmin):
    list_display = ('name','description')
    search_fields = ('name',)
    ordering = ('name',)

@admin.register(AgentLLM)
class AgentLLMAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    ordering = ('name',)



class UsecaseFilter(admin.SimpleListFilter):
    title = 'Usecase'
    parameter_name = 'usecase'

    def lookups(self, request, model_admin):
        return [(usecase.id, usecase.name) for usecase in Usecase.objects.all()]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(usecases__id=self.value())
        return queryset



class AgentForm(forms.ModelForm):
    class Meta:
        model = Agent
        fields = ['name', 'description', 'url', 'usecases', 'llms', 'uploaded_by', 'is_active']

    # Ensure that 'usecases', 'llms', and 'inputs' are required fields
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # We cannot directly set 'inputs' as a field, but we can ensure it's included in the model's related fields.
        self.fields['usecases'].required = True
        self.fields['llms'].required = True
        # We cannot use 'inputs' directly because it's not a field on Agent, but rather a relationship in AgentInput.
        # So, we need to handle this via the related name in the admin, or you could add a custom field to select inputs.
        # In this case, you might want to manually add input selection to the form if needed.

class AgentInputInline(admin.TabularInline):
    model = AgentInput
    extra = 1  # Allows one empty row for new inputs
    fields = ('name', 'agent', 'is_required','input_type','description')
    verbose_name = 'Agent Input'
    verbose_name_plural = 'Agent Inputs'

@admin.register(Agent)
class AgentAdmin(admin.ModelAdmin):
    form = AgentForm  # Use the corrected form
    list_display = ('name', 'description', 'display_llms', 'uploaded_by', 'display_usecases', 'created_at')
    list_filter = (UsecaseFilter, 'created_at','llms')
    search_fields = ('name', 'description')
    autocomplete_fields = ['uploaded_by']  # Adjust this if necessary
    filter_horizontal = ('usecases', 'llms',)  # Allows adding/removing use cases and llms via horizontal selector
    inlines = [AgentInputInline]

    def display_usecases(self, obj):
        return ', '.join([usecase.name for usecase in obj.usecases.all()])
    display_usecases.short_description = 'Usecases'

    def display_llms(self, obj):
        return ', '.join([llm.name for llm in obj.llms.all()])
    display_llms.short_description = "Agent's LLMs"

    def save_model(self, request, obj, form, change):
        # Make sure the agent has at least one usecase, llm, and input
        if not obj.usecases.exists() or not obj.llms.exists():
            raise ValueError("Agent must have at least one Usecase and LLM.")
        super().save_model(request, obj, form, change)


@admin.register(AgentInput)
class AgentInputAdmin(admin.ModelAdmin):
    list_display = ('name', 'agent')
    search_fields = ('name',)
    list_filter = ('agent',)
    ordering = ('agent',)
    autocomplete_fields = ('agent',)  # Enables dropdown search for related agents



# Inline Admin to include AgentResponseInput when creating an AgentResponse
class AgentResponseInputInline(admin.TabularInline):
    model = AgentResponseInput
    extra = 1  # Allows one empty row for new inputs
    fields = ('agent_input', 'value', 'is_valid')
    verbose_name = 'Response Input'
    verbose_name_plural = 'Response Inputs'

@admin.register(AgentResponse)
class AgentResponseAdmin(admin.ModelAdmin):
    list_display = ('user', 'agent', 'started_at')
    search_fields = ('user__username', 'agent__name')
    list_filter = ('agent', 'started_at')
    inlines = [AgentResponseInputInline]  # Include response inputs inline when creating an agent response

    def save_model(self, request, obj, form, change):
        # Ensure that at least one response input is created when saving an agent response
        if not obj.response_inputs.exists():
            raise ValueError("AgentResponse must have at least one response input.")
        super().save_model(request, obj, form, change)


# @admin.register(Agent)
# class AgentAdmin(admin.ModelAdmin):
#     list_display = ('name', 'description', 'uploaded_by', 'display_usecases', 'created_at')
#     list_filter = (UsecaseFilter, 'created_at')
#     search_fields = ('name', 'description')
#     autocomplete_fields = ['uploaded_by']  # Adjust this if necessary
#     filter_horizontal = ('usecases',)  # Allows adding/removing use cases via a horizontal selector

#     def display_usecases(self, obj):
#         return ', '.join([usecase.name for usecase in obj.usecases.all()])
#     display_usecases.short_description = 'Usecases'

# @admin.register(AgentInput)
# class AgentInputAdmin(admin.ModelAdmin):
#     list_display = ('name', 'agent')
#     search_fields = ('name',)
#     list_filter = ('agent',)
#     ordering = ('agent',)
#     autocomplete_fields = ('agent',)  # Enables dropdown search for related agents



# @admin.register(Process)
# class ProcessAdmin(admin.ModelAdmin):
#     list_display = ('name', 'agent', 'status', 'started_at', 'completed_at', 'output')
#     search_fields = ('name', 'output')
#     list_filter = ('status', 'started_at', 'completed_at')
#     date_hierarchy = 'started_at'
#     autocomplete_fields = ('agent', )  # Enables dropdown search for related fields

# @admin.register(Chat)
# class ChatAdmin(admin.ModelAdmin):
#     list_display = ('user', 'agent', 'started_at', 'ended_at')
#     search_fields = ('user__username', 'agent__name')
#     list_filter = ('agent', 'started_at', 'ended_at')
#     date_hierarchy = 'started_at'
#     autocomplete_fields = ('user', 'agent')  # Enables dropdown search for related fields


# @admin.register(ChatMessage)
# class ChatMessageAdmin(admin.ModelAdmin):
#     list_display = ('chat', 'sender', 'message', 'timestamp')
#     search_fields = ('message', 'chat__id')
#     list_filter = ('sender', 'timestamp')
#     date_hierarchy = 'timestamp'
#     autocomplete_fields = ('chat',)  # Enables dropdown search for related chats
