from django.conf import settings
from mailjet_rest import Client
import logging
import requests

logger = logging.getLogger(__name__)


def sign_up_newsletter_on_activation(sender, **kwargs):
    if kwargs['request'].data.get('newsletter', False):
        try:
            sign_up_newsletter(kwargs['user'])
        except requests.exceptions.RequestException:
            pass


def sign_up_newsletter(user):
    api_key = settings.ANYMAIL['MAILJET_API_KEY']
    api_secret = settings.ANYMAIL['MAILJET_SECRET_KEY']
    list_id = settings.NEWSLETTER_LIST_ID
    client = Client(auth=(api_key, api_secret))
    data = {'Action': 'addnoforce', 'Contacts': [{'Email': user.email,}]}
    response = client.contactslist_ManageManyContacts.create(id=list_id, data=data)

    if response.status_code >= 400:
        logger.error(
            'Failed to add {} to list {} (status {})'.format(
                user.email, list_id, response.status_code
            )
        )
        response.raise_for_status()
