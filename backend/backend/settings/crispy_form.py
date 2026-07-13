# Crispy Form Theme - Bootstrap 5
from django.contrib.messages import constants as messages
CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"

# For Bootstrap 5, change error alert to 'danger'
MESSAGE_TAGS = {
    messages.ERROR: 'danger',
}
