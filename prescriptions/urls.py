from django.urls import path
from . import views

urlpatterns = [
    path('home/', views.home, name='home'),
    
    # New chat and PDF endpoints
    path('start_chat/<int:disease_id>/', views.start_chat, name='start_chat'),
    path('chat/<int:disease_id>/', views.chat, name='chat'),
     path('download_prescription/', views.download_prescription, name='download_prescription'),



    # Disease CRUD Operations
    path('disease-list/', views.disease_list, name='disease_list'),
    path('add/', views.disease_create, name='disease_create'),
    path('edit/<int:pk>/', views.disease_update, name='disease_update'),
    path('delete/<int:pk>/', views.disease_delete, name='disease_delete'),
    
    
    path('disease/<int:disease_id>/chat/', views.disease_chat, name='disease_chat'),
    path('disease/<int:disease_id>/chat/<int:chat_id>/', views.disease_chat, name='edit_chat'),
    path('chat/delete/<int:chat_id>/', views.chat_delete, name='chat_delete'),
    
    
    path('chat/<int:message_id>/manage-answers/', views.manage_possible_answers, name='manage_possible_answers'),
    path('suggestion/<int:suggestion_id>/delete/', views.delete_possible_answer, name='delete_possible_answer'),
    
    
    path('disease/<int:disease_id>/symptom-medicines/', views.manage_symptom_medicines, name='manage_symptom_medicines'),
    path('symptom-medicine/delete/', views.delete_symptom_medicine, name='delete_symptom_medicine'),
]