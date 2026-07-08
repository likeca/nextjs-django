import os
import sys
import shutil
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.utils.translation import gettext as _
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views import generic

from . import forms
from . import models


class ProfileShow(LoginRequiredMixin, generic.TemplateView):
    template_name = 'profiles/profile_show.html'
    http_method_names = ['get']

    def get(self, request, *args, **kwargs):
        try:
            slug = kwargs.get('slug')
            if slug:
                profile = get_object_or_404(models.Profile, slug=slug)
                user = profile.user
            else:
                user = request.user

            if user == request.user:
                kwargs['editable'] = True

            kwargs['user'] = user
            return super(ProfileShow, self).get(request, *args, **kwargs)
        except Exception as error:
            messages.error(request, f'Show profile error - {error}')
            return redirect('home')


class ProfileEdit(LoginRequiredMixin, generic.TemplateView):
    template_name = 'profiles/profile_edit.html'
    http_method_names = ['get', 'post']

    def get(self, request, *args, **kwargs):
        try:
            user = request.user
            if 'user_form' not in kwargs:
                kwargs['user_form'] = forms.UserForm(instance=user)
            if 'profile_form' not in kwargs:
                kwargs['profile_form'] = forms.ProfileForm(instance=user.profile)

            return super(ProfileEdit, self).get(request, *args, **kwargs)
        except Exception as error:
            messages.error(request, f'Show edit profile error - {error}')
            return redirect('home')

    def post(self, request, *args, **kwargs):
        try:
            user = request.user
            user_form = forms.UserForm(request.POST, instance=user)
            profile_form = forms.ProfileForm(request.POST, request.FILES, instance=user.profile)

            if not user_form.is_valid() or not profile_form.is_valid():
                if user_form.errors:
                    message = f'Username: {user_form.errors.get_json_data()["username"][0]["message"]}'
                elif profile_form.errors:
                    message = _('Upload unsupported image. Supported image file format: *.png, *.jpg, *.jpeg, *.bmp.')

                messages.error(request, message)
                user_form = forms.UserForm(instance=user)
                profile_form = forms.ProfileForm(instance=user.profile)
                return super(ProfileEdit, self).get(request, user_form=user_form, profile_form=profile_form)

            # Both forms are fine. Time to save!
            user_form.save()
            profile = profile_form.save(commit=False)

            profile.user = user
            profile.save()

            messages.success(request, _('Profile details saved!'))
            return HttpResponseRedirect(reverse_lazy('profiles:show_self'))
        except Exception as error:
            messages.error(request, f'Post edit profile error - {error}')
            return redirect('home')
