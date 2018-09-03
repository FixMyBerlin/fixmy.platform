from .views import UserCreate
from django.urls import path


urlpatterns = [
    path('', UserCreate.as_view(), name='account-create'),
]
