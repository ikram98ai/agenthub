from django.contrib import admin
from .models import Usecase, Agent, AgentInput, Chat, ChatMessage, Process


@admin.register(Usecase)
class UsecaseAdmin(admin.ModelAdmin):
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


@admin.register(Agent)
class AgentAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'uploaded_by', 'display_usecases', 'created_at')
    list_filter = (UsecaseFilter, 'created_at')
    search_fields = ('name', 'description')
    autocomplete_fields = ['uploaded_by']  # Adjust this if necessary
    filter_horizontal = ('usecases',)  # Allows adding/removing use cases via a horizontal selector

    def display_usecases(self, obj):
        return ', '.join([usecase.name for usecase in obj.usecases.all()])
    display_usecases.short_description = 'Usecases'

@admin.register(AgentInput)
class AgentInputAdmin(admin.ModelAdmin):
    list_display = ('name', 'agent')
    search_fields = ('name',)
    list_filter = ('agent',)
    ordering = ('agent',)
    autocomplete_fields = ('agent',)  # Enables dropdown search for related agents


@admin.register(Chat)
class ChatAdmin(admin.ModelAdmin):
    list_display = ('user', 'agent', 'started_at', 'ended_at')
    search_fields = ('user__username', 'agent__name')
    list_filter = ('agent', 'started_at', 'ended_at')
    date_hierarchy = 'started_at'
    autocomplete_fields = ('user', 'agent')  # Enables dropdown search for related fields


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ('chat', 'sender', 'message', 'timestamp')
    search_fields = ('message', 'chat__id')
    list_filter = ('sender', 'timestamp')
    date_hierarchy = 'timestamp'
    autocomplete_fields = ('chat',)  # Enables dropdown search for related chats


@admin.register(Process)
class ProcessAdmin(admin.ModelAdmin):
    list_display = ('name', 'agent', 'status', 'started_at', 'completed_at', 'output')
    search_fields = ('name', 'output')
    list_filter = ('status', 'started_at', 'completed_at')
    date_hierarchy = 'started_at'
    autocomplete_fields = ('agent', 'chat')  # Enables dropdown search for related fields
