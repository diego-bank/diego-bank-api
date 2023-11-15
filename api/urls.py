from django.urls import path, include
from rest_framework.routers import DefaultRouter
from api import views

router = DefaultRouter()
router.register('accounts', views.AccountViewSet)
router.register('transactions', views.TransactionViewSet)
router.register('cards', views.CardViewSet)

# router.register('search/<int:number>', views.AccountSearchViewSet)

app_name = 'api'

urlpatterns = [
    path('', include(router.urls))
]