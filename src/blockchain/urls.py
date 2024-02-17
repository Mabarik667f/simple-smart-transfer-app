from django.contrib.auth.views import LogoutView
from django.urls import path, include
from .views import *

urlpatterns = [
    path('', Main.as_view(), name='home'),
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginUserView.as_view(), name='login'),
    path('login/', LogoutView.as_view(), name='logout'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('transfer/', SendTransferView.as_view(), name='transfer'),
    path('get-last-transactions/', GetLastTransactionsView.as_view(), name='get_last_transactions')
]