from django.urls import path
from django.views.decorators.cache import cache_page
from .models import Planning
from .views import (
    LikeView,
    PlanningDetail,
    PlanningList,
    PlanningSectionDetail,
    PlanningSectionList,
    ReportView,
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
        cache_page(60 * 60 * 4)(PlanningList.as_view()),
        name='planning-list'
    ),
    path(
        'plannings/<int:pk>',
        PlanningDetail.as_view(),
        name='planning-detail'
    ),
    path(
        'plannings/<int:pk>/likes',
        LikeView.as_view(),
        {'model': Planning},
        name='likes-plannings'
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
    ),
    path(
        'reports',
        ReportView.as_view(),
        name='reports'
    )
]
