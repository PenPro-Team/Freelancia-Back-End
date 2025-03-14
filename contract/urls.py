from django.urls import path
from .views import *

urlpatterns=[
    path('create/', create_contract, name='create_contract'),
    path('user/contracts/<int:user_id>', get_user_contracts, name='get_user_contracts'),
    path('update/<int:contract_id>', update_contract, name='update_contract')

]