from django.contrib.auth import get_user_model
from django.contrib.auth.signals import user_logged_in
from django.db.models.signals import post_save
from django.dispatch import receiver
from . import models

import logging
logger = logging.getLogger('project')

User = get_user_model()


@receiver(post_save, sender=User)
def create_profile_handler(sender, instance, created, **kwargs):
    if not created:
        return
    # Create the profile object, only if it is newly created
    profile = models.Profile(user=instance)
    profile.save()
    logger.info('New user profile for %s created', instance)


@receiver(user_logged_in)
def logged_in_handler(sender, user, request, **kwargs):
    # After user logged in update email_verified to True
    profile = models.Profile.objects.get(user_id=user.id)
    if not profile.email_verified:
        profile.email_verified = True
        profile.save()
    logger.info("%s' Email is Verfied", user)
