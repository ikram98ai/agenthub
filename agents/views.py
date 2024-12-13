from django.views.generic import ListView, DetailView
from django.shortcuts import get_object_or_404
from django.db.models import Q
from django.contrib import messages

from django.urls import reverse_lazy
from django.http import  HttpResponseRedirect
from django.views import View

from .tasks import execute_agent
from .forms import AgentInputForm
from .models import Agent, AgentInput, AgentLLM, Usecase, AgentResponse, AgentResponseInput


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
        agent = self.get_object()
        context['inputs'] = agent.inputs.all()
        context['form'] = AgentInputForm(agent=agent)  # Add the form to the context
        return context



class AgentRunSubmitView(View):
    def post(self, request, *args, **kwargs):
        agent = get_object_or_404(Agent, pk=self.kwargs['pk'])
        form = AgentInputForm(request.POST, request.FILES, agent=agent)

        if form.is_valid():
            user = request.user
            
            # Create an AgentResponse
            response = AgentResponse.objects.create(agent=agent, user=user)

            # Save inputs
            inputs = {}
            for field_name, value in form.cleaned_data.items():
                agent_input_id = int(field_name.split('_')[1])
                agent_input = agent.inputs.get(pk=agent_input_id)
                inputs[agent_input.name] = value

                AgentResponseInput.objects.create(
                    agent_response=response,
                    agent_input=agent_input,
                    value=value
                )

            # Trigger Celery task
            task = execute_agent.delay(agent.name, inputs, response_id=response.id)
            response.output = f"Task ID: {task.id} (Pending)"
            response.completed_at = None
            response.save()

            messages.success(request, "Agent execution started.")
            return HttpResponseRedirect(reverse_lazy('agent-detail', kwargs={'pk': agent.pk}))

        messages.error(request, "Failed to submit inputs.")
        return HttpResponseRedirect(reverse_lazy('agent-detail', kwargs={'pk': agent.pk}))