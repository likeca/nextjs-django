import sys
import requests
from django.conf import settings
from django.contrib import messages
from django.shortcuts import redirect
from django.http import HttpResponseRedirect
from django.utils.translation import gettext as _
from django.views import generic

from django.contrib.auth.mixins import LoginRequiredMixin
from graphene_django.views import GraphQLView

from . import forms
from .utils import SendEmail


class HomePage(generic.TemplateView):
    template_name = 'home.html'


class AboutPage(generic.TemplateView):
    template_name = 'about.html'
    http_method_names = ['get', 'post']

    def get(self, request, *args, **kwargs):
        try:
            kwargs['contact_form'] = forms.ContactForm()
            return super(AboutPage, self).get(request, *args, **kwargs)
        except Exception as error:
            messages.error(request, f'Show about error - {error}')
            return redirect('home')

    def post(self, request, *args, **kwargs):
        try:
            contact_form = forms.ContactForm(request.POST)
            if contact_form.is_valid():
                # Begin reCAPTCHA validation
                recaptcha_response = request.POST.get('g-recaptcha-response')
                data = {'secret': settings.RECAPTCHA_PRIVATE_KEY,
                        'response': recaptcha_response}
                r = requests.post(
                    'https://www.google.com/recaptcha/api/siteverify', data=data)
                result = r.json()
                # End reCAPTCHA validation
                if result['success']:
                    message = 'Email From: {}\n{}'.format(
                        contact_form.cleaned_data['from_email'], contact_form.cleaned_data['message'])
                    SendEmail(
                        subject=contact_form.cleaned_data['subject'], message=message)
                    messages.success(request, _('Email sent!'))
                return HttpResponseRedirect('/about')
            else:
                messages.error(request, _(
                    'There was a problem with the form. Please check the details.'))
                return super(AboutPage, self).get(request, contact_form=contact_form)
        except Exception as error:
            messages.error(request, f'Post about contact error - {error}')
            return redirect('home')


class PrivateGraphQLView(LoginRequiredMixin, GraphQLView):
    pass


class SwaggerPage(generic.TemplateView):
    template_name = 'swagger.html'
