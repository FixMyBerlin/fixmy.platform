from django.urls import path
from .models import Report
from .views import LikedByUserReportList, ReportDetail, ReportList, UnsubscribeView
from fixmyapp.views import LikeView

app_name = 'reports'

# fmt: off
urlpatterns = [
    path(
        'reports',
        ReportList.as_view(),
        name='report-list'
    ),
    path(
        'reports/<int:pk>',
        ReportDetail.as_view(),
        name='report-detail'
    ),
    path(
        'users/me/liked/reports',
        LikedByUserReportList.as_view(),
        name='reports-liked-by-user'
    ),
    path(
        'reports/<int:pk>/likes',
        LikeView.as_view(),
        {'model': Report},
        name='likes-reports',
    ),
    path(
        'reports/unsubscribe/<int:user_id>/<str:access_key>', 
        UnsubscribeView.as_view(), 
        name='unsubscribe-report-update'
    ),
]
# fmt: on
