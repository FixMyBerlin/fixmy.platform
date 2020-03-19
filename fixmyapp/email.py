import djoser.email
import urllib.parse
from django.conf import settings


class ActivationEmail(djoser.email.ActivationEmail):

    def get_context_data(self):
        context = super(ActivationEmail, self).get_context_data()

        if self.request and self.request.data.get('newsletter', False):
            context['url'] = urllib.parse.urljoin(
                context['url'], '?newsletter=yes')

        return context


def template_context(request):
    return {
        "site_name": settings.SITE_NAME
    }
