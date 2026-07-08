from django.urls import path
from . import views

app_name = 'profiles'
urlpatterns = [
    path('me/', views.ProfileShow.as_view(), name='show_self'),
    path('me/edit/', views.ProfileEdit.as_view(), name='edit_self'),
    path('<slug:slug>/', views.ProfileShow.as_view(), name='show')
]
