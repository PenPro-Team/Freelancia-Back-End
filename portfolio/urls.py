from django.urls import path
from . import views


urlpatterns = [
    path('', views.PortfolioView.as_view(), name='portfolio_list'),
    path('<int:id>', views.PortfolioAPI.as_view(), name='portfolio_api'),
]