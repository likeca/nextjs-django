import os
import uuid
from io import BytesIO
from django.db import models
from django.conf import settings
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.core.validators import FileExtensionValidator
from django.utils.deconstruct import deconstructible
from django.utils.translation import gettext_lazy as _
from PIL import Image

from django_countries.fields import CountryField
from backend.constants import PROVINCE

# Local Storage
from django.core.files.storage import FileSystemStorage
@deconstructible
class UploadStorage(FileSystemStorage):
    def __init__(self, *args, **kwargs):
        super(UploadStorage, self).__init__(location=settings.MEDIA_ROOT, base_url='/media/')

# Remote Storage
# from storages.backends.s3boto3 import S3Boto3Storage
# @deconstructible
# class UploadStorage(S3Boto3Storage):
#     location = 'media'


def upload_to(instance, filename):      # Convert to (private) path, not full private yet
    profile_img = f'users/{instance.user.profile.slug}/profile_pics/{filename}'
    profile_img_path = os.path.join(settings.MEDIA_ROOT, profile_img)
    if os.path.exists(profile_img_path):
        os.remove(profile_img_path)
    return profile_img


class BaseProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, primary_key=True, on_delete=models.CASCADE)
    slug = models.UUIDField(default=uuid.uuid4, blank=True, editable=False)
    # Add more user profile fields here with default values,
    # CharFiled and TextFiled discouraged to use null=True in Django, avoid two possible values for “no data”: null and the empty string
    # python manage.py makemigrations profiles --name AddProfileModels
    avatar = models.ImageField(_('Avatar Picture'), upload_to=upload_to, storage=UploadStorage(), blank=True, null=True, validators=[FileExtensionValidator(['png', 'jpg', 'jpeg', 'bmp', 'gif'])])
    bio = models.CharField(_('Short Bio'), max_length=200, blank=True)
    email_verified = models.BooleanField(_('Email Verified'), default=False)
    phone_number = models.CharField(_('Phone Number'), max_length=20, blank=True)
    pobox = models.CharField(_('P.O. Box'), max_length=20, blank=True)
    apt_unit = models.CharField(_('Apt/Unit'), max_length=20, blank=True)
    street_num = models.CharField(_('Street Number'), max_length=20, blank=True)
    street_name = models.CharField(_('Street Name'), max_length=50, blank=True)
    city = models.CharField(_('City/Town'), max_length=30, blank=True)
    # subdivision = models.CharField(_('Province'), max_length=2, blank=True, db_index=True, choices=PROVINCE)    # For Territory, Province, State, District, etc.
    # For Territory, Province, State, District, etc.
    province = models.CharField(_('Province'), max_length=2, blank=True, db_index=True, choices=PROVINCE)
    country = CountryField(default='CA')
    post_code = models.CharField(_('Postal Code'), max_length=7, blank=True)

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        if self.avatar:
            image = Image.open(BytesIO(self.avatar.read()))
            image.thumbnail((140, 140))
            output = BytesIO()
            image.save(output, format='PNG')
            output.seek(0)
            self.avatar = InMemoryUploadedFile(output, 'ImageField', 'avatar.png', 'image/png', len(output.getvalue()), None)
        super(BaseProfile, self).save(*args, **kwargs)


class Profile(BaseProfile):
    def __str__(self):
        return f"{self.user}'s profile"
