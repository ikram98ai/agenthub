from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import Agent, Chat, ChatMessage, Usecase, AgentInput, AgentLLM
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q

def agent_list(request):
    agents = Agent.objects.all()
    search_query = request.GET.get("q", "")
    usecase_filter = request.GET.get("usecase", "")
    llm_filter = request.GET.get("llm", "")

    # Apply search filter
    if search_query:
        agents = agents.filter(Q(name__icontains=search_query) | Q(description__icontains=search_query))

    # Apply usecase filter
    if usecase_filter:
        agents = agents.filter(usecases__id=usecase_filter)

    # Apply LLM filter
    if llm_filter:
        agents = agents.filter(llms__id=llm_filter)

    # Remove duplicates in the queryset
    agents = agents.distinct()

    # Pagination
    paginator = Paginator(agents, 10)  # 10 agents per page
    page = request.GET.get("page", 1)
    try:
        agents_page = paginator.page(page)
    except PageNotAnInteger:
        agents_page = paginator.page(1)  # Return the first page
    except EmptyPage:
        if request.headers.get('hx-request'):  # If HTMX request for invalid page
            return render(request, 'partials/empty_page.html')  # Render empty response for infinite scroll
        agents_page = paginator.page(paginator.num_pages)  # Return last page

    context = {
        "agents": agents_page,
        "usecases": Usecase.objects.all(),
        "llms": AgentLLM.objects.all(),
        "page_obj": agents_page,
    }

    if request.headers.get('hx-request'):  # HTMX partial page response
        return render(request, "partials/agent_list.html", context)

    return render(request, "agents/agent_list.html", context)



@login_required
def chat_view(request, agent_id):
    agent = get_object_or_404(Agent, id=agent_id)
    chat, created = Chat.objects.get_or_create(user=request.user, agent=agent, ended_at__isnull=True)
    return render(request, 'agents/chat.html', {'agent': agent, 'chat': chat})

@login_required
def send_message(request, chat_id):
    chat = get_object_or_404(Chat, id=chat_id, user=request.user)
    message_text = request.POST.get('message', '')
    ChatMessage.objects.create(chat=chat, sender='user', message=message_text)

    # Simulate agent response
    agent_response = f"Response from agent to: {message_text}"  # Placeholder for agent API call
    ChatMessage.objects.create(chat=chat, sender='agent', message=agent_response)

    return JsonResponse({
        'user_message': message_text,
        'agent_response': agent_response,
    })
