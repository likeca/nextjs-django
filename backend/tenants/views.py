from datetime import datetime
import requests
import sys
from pathlib import Path
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect
from django.utils.translation import gettext as _
from django.urls import reverse_lazy
from django.views.generic import TemplateView


# class DashboardView(LoginRequiredMixin, TemplateView):
class DashboardView(TemplateView):
    template_name = 'tenants/dashboard.html'
    http_method_names = ['get']

    def get(self, request, *args, **kwargs):
        try:
            user = request.user
            kwargs['user'] = user
            return super(DashboardView, self).get(request, *args, **kwargs)
        except Exception as error:
            messages.error(request, f'Show tenants error - {error}')
            return redirect('home')


# class ChannelsView(LoginRequiredMixin, TemplateView):
#     template_name = 'tenants/channels.html'
#     http_method_names = ['get', 'post']

#     def get(self, request, *args, **kwargs):
#         try:
#             admin_user = request.user
#             if admin_user.is_staff:       # Tenant Administrators
#                 result = get_groups(admin_user)
#                 if result['status'] == 'success':
#                     kwargs['groups'] = result['groups']
#                 else:
#                     kwargs['groups'] = []
#             else:
#                 return redirect('home')
#             return super(ChannelsView, self).get(request, *args, **kwargs)
#         except Exception as error:
#             messages.error(request, f'Show groups error - {error}')
#             return redirect('home')

#     def post(self, request, *args, **kwargs):
#         try:
#             admin_user = request.user
#             if admin_user.is_staff:       # Tenant Administrators
#                 print(request.POST.get('action'))
#                 print(request.POST.get('channel_name'))
#                 if request.POST.get('action') == 'Add Channel':
#                     result = group_actions(admin_user, request.POST.get('action'), request.POST.get('channel_name'))
#                 elif request.POST.get('action') == 'Modify Channel':
#                     result = group_actions(admin_user, request.POST.get('action'), request.POST.get('channel_name'))
#                 print(result)
#                 if result['status'] == 'success':
#                     if request.POST.get('action') == 'Add Channel':
#                         messages.success(request, _('Add channel success!'))
#                     elif request.POST.get('action') == 'Modify Channel':
#                         messages.success(request, _('Modify channel success!'))
#                     return HttpResponseRedirect(reverse_lazy('tenants:channels'))
#                 else:
#                     messages.error(request, result['status'])
#             else:
#                 return redirect('home')
#             messages.success(request, _('Channel edit success!'))
#             return HttpResponseRedirect(reverse_lazy('tenants:channels'))
#         except Exception as error:
#             messages.error(request, f'Edit channel error - {error}')
#             return redirect('home')


# class UsersView(LoginRequiredMixin, TemplateView):
#     template_name = 'tenants/users.html'
#     http_method_names = ['get', 'post']

#     def get(self, request, *args, **kwargs):
#         try:
#             response = requests.get('https://takserver-002.stg.kwesst.cloud:8443/Marti/api/certadmin/cert/', verify=(Path(settings.BASE_DIR, 'tenants/kwesst/intermediate-ca.pem')),
#                                     cert=(Path(settings.BASE_DIR, 'tenants/kwesst/admin.pem'), Path(settings.BASE_DIR, 'tenants/kwesst/admin.decrypted.key')))
#             cert_data = sorted(response.json()['data'], key=lambda x: x['userDn'])
#             api_date_format = '%Y-%m-%dT%H:%M:%S.%f%z'

#             admin_user = request.user
#             if admin_user.is_staff:       # Tenant Administrators
#                 result = get_users(admin_user)
#                 if result['status'] == 'success':
#                     kwargs['users'] = result['users']
#                     i = 0
#                     for user in kwargs['users']:
#                         devices = []
#                         for cert in cert_data:
#                             if cert['userDn'] == user['username']:
#                                 devices.append({
#                                     'id': cert['id'],
#                                     'clientUid': cert['clientUid'],
#                                     'serialNumber': cert['serialNumber'],
#                                     'issuanceDate': datetime.strptime(cert['issuanceDate'], api_date_format),
#                                     'expirationDate': datetime.strptime(cert['expirationDate'], api_date_format),
#                                     'revocationDate': datetime.strptime(cert['revocationDate'], api_date_format) if cert['revocationDate'] else None,
#                                 })
#                         kwargs['users'][i]['devices'] = devices
#                         i += 1
#                 else:
#                     kwargs['users'] = []
#                     messages.error(request, f'Show users error - {result["status"]}')
#             else:
#                 return redirect('home')
#             return super(UsersView, self).get(request, *args, **kwargs)
#         except Exception as error:
#             messages.error(request, f'Show users error - {error}')
#             return redirect('home')

#     def post(self, request, *args, **kwargs):
#         try:
#             admin_user = request.user
#             if admin_user.is_staff:       # Tenant Administrators
#                 if request.POST.get('action') == 'Add User':
#                     result = user_actions(admin_user, request.POST.get('action'), request.POST.get('username'), request.POST.get('password'))
#                 else:
#                     result = user_actions(admin_user, request.POST.get('action'), request.POST.get('username'))
#                 print(result)
#                 if result['status'] == 'success':
#                     if request.POST.get('action') == 'Enable User':
#                         messages.success(request, _('Enable user success!'))
#                     elif request.POST.get('action') == 'Disable User':
#                         messages.success(request, _('Disable user success!'))
#                     elif request.POST.get('action') == 'Delete User':
#                         messages.success(request, _('Delete user success!'))
#                     return HttpResponseRedirect(reverse_lazy('tenants:users'))
#                 else:
#                     messages.error(request, result['status'])
#             else:
#                 return redirect('home')
#             messages.success(request, _('User edit success!'))
#             return HttpResponseRedirect(reverse_lazy('tenants:users'))
#         except Exception as error:
#             messages.error(request, f'Edit user error - {error}')
#             return redirect('home')
