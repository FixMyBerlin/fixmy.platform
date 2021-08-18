from django.urls import path
from .views import (
    SignupView,
    StationList,
    SurveyBicycleUsageView,
    SurveyStationView,
    StationSurveysByUUID,
)

app_name = 'fahrradparken'

urlpatterns = [
    path(
        'signup',
        SignupView.as_view(),
        name='fahrradparken-signups',
    ),
    path('stations', StationList.as_view(), name='fahrradparken-stations'),
    path(
        'survey/station',
        SurveyStationView.as_view(),
        name='fahrradparken-survey-station',
    ),
    path(
        'survey/bicycle-usage',
        SurveyBicycleUsageView.as_view(),
        name='fahrradparken-survey-bicycle-usage',
    ),
    path(
        'uuid/<uuid:session>',
        StationSurveysByUUID.as_view(),
        name='fahrradparken-survey-station-by-user',
    ),
]
