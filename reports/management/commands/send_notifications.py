from collections import defaultdict
from django.conf import settings
from django.core.mail import get_connection, EmailMultiAlternatives
from django.core.management.base import BaseCommand
from django.template.loader import get_template

from fixmyapp.models import NoticeSetting
from reports.models import StatusNotice, Report


class Command(BaseCommand):
    help = 'Send queued notifications for report status updates'
    email_data = []
    template_txt = get_template("email/report_update.txt")

    def handle(self, *args, **options):
        all_notices = StatusNotice.objects.select_related().order_by('user_id').all()

        user_notices = defaultdict(list)
        for i, notice in enumerate(all_notices):
            user_notices[notice.status].append(notice)
            is_last_notice = len(all_notices) == (i + 1)
            is_next_user_different = (
                is_last_notice or all_notices[i + 1].user != notice.user
            )
            if is_last_notice or is_next_user_different:
                self.render_email(notice.user, user_notices)
                user_notices = defaultdict(list)
        self.send_all()

    def render_email(self, user, collection):
        if len(collection) == 0 or StatusNotice.user_preference(user) is False:
            # user disabled notifications
            return

        unsubscribe_url = StatusNotice.unsubscribe_url(user).replace(
            "/api/", f"{settings.FRONTEND_URL}/api/v1/"
        )

        data = self.template_data(collection)
        subject = "Updates"
        body_txt = self.template_txt.render(
            context={"user": user, "unsubscribe_url": unsubscribe_url, **data}
        )
        body_html = None
        self.email_data.append(
            (subject, body_txt, body_html, settings.DEFAULT_FROM_EMAIL, [user.email])
        )

    def send_all(self):
        connection = get_connection()
        messages = []
        for subject, text, html, from_email, recipient in self.email_data:
            message = EmailMultiAlternatives(subject, text, from_email, recipient)
            # message.attach_alternative(html, 'text/html')
            messages.append(message)
        return connection.send_messages(messages)

    def template_data(self, collection):
        """Collect data needed for rendering template"""

        data = {}
        for status in [
            Report.STATUS_PLANNING,
            Report.STATUS_REPORT_REJECTED,
            Report.STATUS_REPORT_ACCEPTED,
            Report.STATUS_EXECUTION,
            Report.STATUS_DONE,
        ]:
            if len(collection[status]) == 0:
                data[status] = None
            else:
                data[status] = dict()
                data[status]["is_single"] = len(collection[status]) == 1

                if len(collection[status]) == 1:
                    first = collection[status][0]
                    data[status]["first_address"] = first.report.address
                    data[status]["first_url"] = first.report.frontend_url
                    data[status]["first_reason"] = (
                        f": {first.report.status_reason}"
                        if (
                            first.report.status_reason
                            and len(first.report.status_reason) > 0
                        )
                        else "."
                    )
                data[status]["count"] = len(collection[status])
                data[status]["notices"] = collection[status]

        return data

