from django.urls import path
from . import views 

app_name = 'chatbot' 

urlpatterns = [
    path('ask/', views.ask_question_api, name='ask_question_api'),
    path('feedback/', views.submit_feedback_api, name='chatbot_feedback'),
]
