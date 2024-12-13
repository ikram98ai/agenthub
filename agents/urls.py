# urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.AgentListView.as_view(), name='agent-list'),
    path('agents/<int:pk>/', views.AgentDetailView.as_view(), name='agent-detail'),
    path('agents/<int:pk>/run/', views.AgentRunSubmitView.as_view(), name='agent-run'),
    # path('agents/<int:pk>/run/', views.AgentRunView.as_view(), name='agent-run'),

]
