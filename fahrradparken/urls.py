from django.urls import path
from .views import SignupView, EventSignupView

app_name = 'fahrradparken'

urlpatterns = [
    path(
        'signups',
        SignupView.as_view(),
        name='fahrradparken-signups',
    ),
    path(
        'event-signups',
        EventSignupView.as_view(),
        name='fahrradparken-signups',
    ),
]
