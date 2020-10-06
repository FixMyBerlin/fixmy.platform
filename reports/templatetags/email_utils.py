from django import template
from django.utils.html import conditional_escape
from django.utils.safestring import mark_safe

register = template.Library()


@register.filter(is_safe=True)
def linked_plannings(report):
    """Formats a list of linked plannings for a report or return empty string"""

    def address_link(planning):
        return f"<a href='{planning.frontend_url}'>{conditional_escape(planning.address)}</a>"

    num_plannings = report.plannings.count()
    if num_plannings == 0:
        return ""
    elif num_plannings == 1:
        return mark_safe(
            f"- Informationen zum alternativen Standort finden Sie auf der Detailseite {address_link(report.plannings.first())}."
        )
    else:
        listing = ", ".join([address_link(p) for p in report.plannings.all()])
        return mark_safe(
            f"- Informationen zu den alternativen Standorten finden Sie auf den folgenden Detailseiten: {listing}."
        )
