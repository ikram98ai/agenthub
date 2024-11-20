from django.urls import path
from . import views

urlpatterns = [
    path('', views.agent_list, name='agent_list'),
    path('chat/<int:agent_id>/', views.chat_view, name='chat_view'),
    path('chat/<int:chat_id>/send/', views.send_message, name='send_message'),
]
