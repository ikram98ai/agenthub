from django.contrib import admin
from .models import Usecase,AgentLLM, Agent, AgentInput, AgentResponse, AgentResponseInput


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



class AgentInputInline(admin.TabularInline):
    model = AgentInput
    extra = 1  # Allows one empty row for new inputs
    fields = ('name', 'agent', 'is_required','input_type','description')
    verbose_name = 'Agent Input'
    verbose_name_plural = 'Agent Inputs'

@admin.register(Agent)
class AgentAdmin(admin.ModelAdmin):
    # form = AgentForm  # Use the corrected form
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

  


# Inline Admin to include AgentResponseInput when creating an AgentResponse
class AgentResponseInputInline(admin.TabularInline):
    model = AgentResponseInput
    extra = 1  # Allows one empty row for new inputs
    fields = ('agent_input', 'value', 'is_valid')
    verbose_name = 'Response Input'
    verbose_name_plural = 'Response Inputs'

@admin.register(AgentResponse)
class AgentResponseAdmin(admin.ModelAdmin):
    list_display = ('user', 'agent', 'started_at','status','display_output')
    search_fields = ('user__username', 'agent__name')
    list_filter = ('agent', 'started_at')
    inlines = [AgentResponseInputInline]  # Include response inputs inline when creating an agent response

    def display_output(self, obj):
        return obj.output[:100] if obj.output else ''
    display_output.short_description = "Agent's output"

    def save_model(self, request, obj, form, change):
        # Ensure that at least one response input is created when saving an agent response
        if not obj.response_inputs.exists():
            raise ValueError("AgentResponse must have at least one response input.")
        super().save_model(request, obj, form, change)
