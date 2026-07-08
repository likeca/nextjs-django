from django import forms
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Field

from . import models


class UserForm(forms.ModelForm):
    class Meta:
        model = get_user_model()
        # custom user is email-based (no username); expose name instead
        fields = ['name']

    def __init__(self, *args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.layout = Layout(Field('name'))


class ProfileForm(forms.ModelForm):
    class Meta:
        model = models.Profile
        fields = [
            'bio', 'avatar', 'phone_number', 'pobox', 'apt_unit', 'street_num', 'street_name', 'city', 'province', 'country', 'post_code'
        ]

    def __init__(self, *args, **kwargs):
        super(ProfileForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False

        self.helper.layout = Layout(
            Field('bio'),
            Field('avatar'),
            Field('phone_number'),
            Field('pobox'),
            Field('apt_unit'),
            Field('street_num'),
            Field('street_name'),
            Field('city'),
            Field('province'),
            Field('country'),
            Field('post_code'),
            Submit('update', _('Update'), css_class='btn-primary'),
        )
