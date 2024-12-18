from django.views.generic import ListView, DetailView
from django.db.models import Q
from django.views import View

from .tasks import execute_agent
from .forms import AgentInputForm
from .models import Agent, AgentInput, AgentLLM, Usecase, AgentResponse, AgentResponseInput
from django.db.models import Prefetch

from django.views.generic import View
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.core.cache import cache
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie

class AgentRunSubmitView(View):
    @method_decorator(ensure_csrf_cookie)
    def post(self, request, *args, **kwargs):
        agent = get_object_or_404(Agent.objects.select_related('uploaded_by'), 
                                pk=self.kwargs['pk'])
        
        # Rate limiting
        rate_limit_key = f"agent_run_{request.user.id}_{agent.id}"
        if cache.get(rate_limit_key):
            return JsonResponse({
                'error': 'Please wait before submitting another request'
            }, status=429)
        
        form = AgentInputForm(request.POST, request.FILES, agent=agent)
        
        if form.is_valid():
            # Set rate limit
            cache.set(rate_limit_key, True, 60)  # 1 minute cooldown
            
            response = AgentResponse.objects.create(
                agent=agent,
                user=request.user,
                status='pending'
            )
            
            # Process inputs
            inputs = {}
            input_objects = []
            
            for field_name, value in form.cleaned_data.items():
                agent_input_id = int(field_name.split('_')[1])
                agent_input = agent.inputs.get(pk=agent_input_id)
                inputs[agent_input.name] = value
                
                input_objects.append(
                    AgentResponseInput(
                        agent_response=response,
                        agent_input=agent_input,
                        value=value
                    )
                )
            
            # Bulk create input records
            AgentResponseInput.objects.bulk_create(input_objects)
            
            # Trigger Celery task
            task = execute_agent.delay(agent.name, inputs, response_id=response.id)
            
            return JsonResponse({
                'status': 'success',
                'response_id': response.id,
                'task_id': task.id
            })
            
        return JsonResponse({
            'status': 'error',
            'errors': form.errors
        }, status=400)
    


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

        responses = (
            AgentResponse.objects
            .filter(agent=agent, user=self.request.user)
            .select_related('agent', 'user')
            .prefetch_related(
                Prefetch(
                    'response_inputs',
                    queryset=AgentResponseInput.objects.select_related('agent_input')  # Optimize nested FK
                )
            )
        )

        context['inputs'] = agent.inputs.all()
        context['responses'] = responses

        context['form'] = AgentInputForm(agent=agent)  # Add the form to the context
        return context


