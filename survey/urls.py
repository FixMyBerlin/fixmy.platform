from django.urls import path
from .views import SurveyView

urlpatterns = [
    path(
        '<int:project>/<uuid:session>',
        SurveyView.as_view(),
        name='add-survey'
    ),
]
