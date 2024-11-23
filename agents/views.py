from django.views.generic import ListView, DetailView
from django.shortcuts import render
from .models import Agent, AgentLLM, Usecase, AgentInput
from django.db.models import Q
from django.contrib import messages

class AgentListView(ListView):
    model = Agent
    template_name = 'agents/agent_list.html'
    context_object_name = 'agents'
    paginate_by = 8  # Show 8 agents per page
    
    def get_queryset(self):
        queryset = Agent.objects.all().prefetch_related('llms', 'usecases')
        
        # Search functionality
        search_query = self.request.GET.get('search', '')
        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query) |
                Q(description__icontains=search_query)
            )
        
        # LLM filter
        llm_filter = self.request.GET.getlist('llm')
        if llm_filter:
            queryset = queryset.filter(llms__id__in=llm_filter).distinct()
            
        # Use case filter
        usecase_filter = self.request.GET.getlist('usecase')
        if usecase_filter:
            queryset = queryset.filter(usecases__id__in=usecase_filter).distinct()
            
        # Status filter
        status = self.request.GET.get('status')
        if status == 'active':
            queryset = queryset.filter(is_active=True)
        elif status == 'inactive':
            queryset = queryset.filter(is_active=False)
            
        # Sorting
        sort_by = self.request.GET.get('sort', 'name')
        if sort_by == 'name':
            queryset = queryset.order_by('name')
        elif sort_by == 'created':
            queryset = queryset.order_by('-created_at')
        elif sort_by == 'updated':
            queryset = queryset.order_by('-updated_at')
            
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Add filter options to context
        context['llms'] = AgentLLM.objects.all()
        context['use_cases'] = Usecase.objects.all()
        
        # Add current filter states to context
        context['current_filters'] = {
            'search': self.request.GET.get('search', ''),
            'llm': self.request.GET.getlist('llm'),
            'usecase': self.request.GET.getlist('usecase'),
            'status': self.request.GET.get('status', ''),
            'sort': self.request.GET.get('sort', 'name'),
        }
        
        # Add counts for summary
        context['total_agents'] = Agent.objects.count()
        context['active_agents'] = Agent.objects.filter(is_active=True).count()
        
        # Convert filter IDs to lists of integers for template comparison
        context['selected_llms'] = [int(x) for x in self.request.GET.getlist('llm')]
        context['selected_usecases'] = [int(x) for x in self.request.GET.getlist('usecase')]
        
        return context



class AgentDetailView(DetailView):
    model = Agent
    template_name = 'agents/agent_detail.html'
    context_object_name = 'agent'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['inputs'] = self.object.inputs.all()
        return context
