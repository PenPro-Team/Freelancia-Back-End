
from django.urls import path
from . import views

urlpatterns = [
    path('create_review/', views.create_review),
    path('get_reviews/<int:user_id>', views.get_reviews),
    path('update_review/<int:review_id>', views.update_review),
    path('delete_review/<int:review_id>', views.delete_review),   
]
