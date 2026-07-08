from django.urls import path
from . import views

app_name = 'tenants'
urlpatterns = [
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),
    # path('channels/', views.ChannelsView.as_view(), name='channels'),
    # path('users/', views.UsersView.as_view(), name='users'),
]
