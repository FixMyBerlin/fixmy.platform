from django.urls import path
from .views import (
    CheckPreviousBicycleSurvey,
    ParkingFacilityListView,
    ParkingFacilityView,
    PhotoUploadView,
    RawBicycleUsageSurveyListing,
    RawStationSurveyListing,
    SignupView,
    StationList,
    StationView,
    SurveyBicycleUsageView,
    SurveyInfoView,
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
    path('info', SurveyInfoView.as_view()),
    path('stations/<int:pk>', StationView.as_view(), name='fahrradparken-stations'),
    path('stations', StationList.as_view(), name='fahrradparken-stations'),
    path(
        'survey/station',
        SurveyStationView.as_view(),
        name='fahrradparken-survey-station',
    ),
    path(
        'survey/photo/<str:fname>',
        PhotoUploadView.as_view(),
        name='fahrradparken-photo-upload',
    ),
    path(
        'survey/bicycle-usage',
        SurveyBicycleUsageView.as_view(),
        name='fahrradparken-survey-bicycle-usage',
    ),
    path(
        'uuid/<uuid:session>',
        StationSurveysByUUID.as_view(),
        name='fahrradparken-survey-station-by-session',
    ),
    path(
        'uuid/<uuid:session>/bicycle-usage-survey',
        CheckPreviousBicycleSurvey.as_view(),
        name='fahrradparken-previous-bicycle-survey-by-session',
    ),
    path(
        'survey-results/stations',
        RawStationSurveyListing.as_view(),
    ),
    path(
        'survey-results/bicycle-usage',
        RawBicycleUsageSurveyListing.as_view(),
    ),
    path(
        'parking-facilities',
        ParkingFacilityListView.as_view(),
        name='fahrradparken-parking-facility-list',
    ),
    path(
        'parking-facilities/<int:pk>',
        ParkingFacilityView.as_view(),
        name='fahrradparken-parking-facility',
    ),
]
