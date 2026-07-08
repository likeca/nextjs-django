from django.conf import settings


def global_settings(request):
    # return any necessary values
    return {
        'GOOGLE_MEASUREMENT_ID': settings.GOOGLE_MEASUREMENT_ID,
        'RECAPTCHA_PUBLIC_KEY': settings.RECAPTCHA_PUBLIC_KEY,
        'SITE_NAME': settings.SITE_NAME,
        'SITE_URL': settings.SITE_URL
    }