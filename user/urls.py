from django.urls import path
from user import views

app_name = 'user'
url_paterns = [
    path('create/', views.CreateUserAPIView.as_view(), name='create-user'),
    path('me/', views.ManagerUserAPIView.as_view(), name='me'),
]