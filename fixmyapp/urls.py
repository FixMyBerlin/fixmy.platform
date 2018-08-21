from django.urls import path
from .views import (
    PlanningDetail,
    PlanningList,
    PlanningSectionDetail,
    PlanningSectionList,
    feedback,
    profile
)


urlpatterns = [
    path(
        'feedback',
        feedback,
        name='feedback'
    ),
    path(
        'plannings',
        PlanningList.as_view(),
        name='planning-list'
    ),
    path(
        'plannings/<int:pk>',
        PlanningDetail.as_view(),
        name='planning-detail'
    ),
    path(
        'planning-sections',
        PlanningSectionList.as_view(),
        name='planningsection-list'
    ),
    path(
        'planning-sections/<int:pk>',
        PlanningSectionDetail.as_view(),
        name='planningsection-detail'
    ),
    path(
        'profiles/<str:profile_id>',
        profile,
        name='profile-detail'
    )
]
