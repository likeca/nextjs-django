from django.conf import settings
from django.core.mail import send_mail

import logging
logger = logging.getLogger('project')


def SendEmail(subject, message, to=None, files=None):
    try:
        if to:
            email_to = to
        else:
            email_to = settings.WEBMASTERS
        send_mail(
            subject,
            message,
            settings.EMAIL_HOST_USER,
            email_to,
            fail_silently=False,
        )
    except Exception as e:
        if to:
            email_to = to
        else:
            email_to = settings.WEBMASTERS
        logger.info('Error - send_email: {} - '.format(e, subject))
        send_mail(
            f'Error - {subject}',
            message,
            settings.EMAIL_HOST_USER,
            email_to,
            fail_silently=False,
        )
