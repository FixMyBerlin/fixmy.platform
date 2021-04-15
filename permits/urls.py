from django.urls import path
from .views import EventPermitView, EventPermitDocumentView

app_name = 'permits'

# fmt: off
urlpatterns = [
    path(
        'permits/events/<str:campaign>',
        EventPermitView.as_view(),
        name='permits-events'
    ),
    path(
        'permits/events/<str:campaign>/<int:pk>',
        EventPermitView.as_view(),
        name='permits-events-detail'
    ),
    path(
        'permits/events/<str:campaign>/<str:doc_name>/<str:fname>',
        EventPermitDocumentView.as_view(),
        name='permits-events-document'
    ),
]
# fmt: on
