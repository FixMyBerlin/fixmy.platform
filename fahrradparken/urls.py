from django.urls import path
from .views import SignupView, StationList

app_name = 'fahrradparken'

urlpatterns = [
    path(
        'signup',
        SignupView.as_view(),
        name='fahrradparken-signups',
    ),
    path('stations', StationList.as_view(), name='fahrradparken-stations'),
]
