from django.urls import path
from .views import SurveyView, add_rating

urlpatterns = [
    path(
        '<int:project>/<uuid:session>',
        SurveyView.as_view(),
        name='add-survey'
    ),
    path(
        '<int:project>/<uuid:session>/ratings/<str:scene_id>',
        add_rating,
        name='add-rating'
    ),
]
