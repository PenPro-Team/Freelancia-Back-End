
from django.urls import path
from . import views

urlpatterns = [
    path('create', views.create_review, name='create_review'),
    path('received/user/<int:user_id>', views.get_reviews, name='get_reviews'),
    path('update/<int:review_id>', views.update_review, name='update_review'),
    path('delete/<int:review_id>', views.delete_review, name='delete_review'),
    path('made/user/<int:user_id>', views.get_user_reviwes, name='get_user_reviwes'),
    path('project/<int:project_id>', views.get_project_reviews, name='get_project_reviews'),   
]
