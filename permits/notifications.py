from datetime import date, timedelta
from django.conf import settings
from django.core import mail
from django.template.loader import render_to_string

from permits.models import EventPermit


def send_decision_notice(application):
    """Send notice informing the applicant about being accepted/rejected

    Make sure to save the instance after calling this method as the date of
    the decision is recorded on call.
    """

    if application.status == EventPermit.STATUS_ACCEPTED:
        # Areas in a park area need to have a specific park area set for a
        # permit to be sent
        if (
            application.area_category == EventPermit.LOCATION_PARK
            and application.area_park_name == None
        ):
            raise AttributeError("Park zone permit missing park zone selection")

        context = {
            "is_park_zone": application.area_category == EventPermit.LOCATION_PARK,
            "is_parking_zone": application.area_category
            == EventPermit.LOCATION_PARKING,
            "applicant_email": application.email,
            "link_permit": application.permit_url,
            "link_traffic_order": application.traffic_order_url,
        }
        subject = (
            "Ihr Antrag auf eine Sondernutzung für eine Veranstaltung – Xhain-Terrassen"
        )
        body = render_to_string("xhain/notice_event_accepted.txt", context=context)
    elif application.status == EventPermit.STATUS_REJECTED:
        try:
            context = {
                "applicant_email": application.email,
                "application_created": application.created_date.date(),
                "application_received": application.application_received.date(),
                "legal_deadline": date.today() + timedelta(days=14),
                "title": application.title,
                "full_name": f"{application.first_name} {application.last_name}",
                "rejection_reason": application.note,
            }
            pass
        except AttributeError:
            raise AttributeError("Missing data")

        if application.note is None or len(application.note) == 0:
            raise AttributeError("Missing note")

        subject = "Ihr Antrag auf eine Sondernutzungserlaubnis Xhain-Terrassen "
        body = render_to_string("xhain/notice_event_rejected.txt", context=context)
    else:
        raise ValueError("Invalid status for sending notice email")

    mail.send_mail(
        subject, body, settings.DEFAULT_FROM_EMAIL, [settings.GASTRO_RECIPIENT]
    )

    try:
        application.set_application_decided()
    except KeyError:
        raise AttributeError("Campaign missing permit date range")


def send_registration_confirmation(self, recipient, request):
    """Send a registration confirmation email notice"""
    subject = 'Ihr Antrag bei Xhain-Terrassen'
    body = render_to_string('xhain/notice_event_registered.txt', request=request)
    mail.send_mail(
        subject, body, settings.DEFAULT_FROM_EMAIL, [recipient], fail_silently=True
    )