from django.urls import path
from user import views

app_name = 'user'
urlpatterns = [
    path('create/', views.CreateUserAPIView.as_view(), name='create-user'),
    path('me/', views.ManagerUserAPIView.as_view(), name='me'),
]