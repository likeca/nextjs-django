# from django.contrib.auth.models import User, Group
# from django.contrib.auth.mixins import LoginRequiredMixin
# from rest_framework.authentication import SessionAuthentication, TokenAuthentication
# from tokenize import group
# from .serializers import UserSerializer, GroupSerializer

from django.conf import settings
from rest_framework import permissions
from rest_framework.authentication import TokenAuthentication
from rest_framework.views import APIView
from rest_framework.response import Response

from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from dj_rest_auth.registration.views import SocialLoginView


class GoogleSignin(SocialLoginView):
    adapter_class = GoogleOAuth2Adapter
    client_class = OAuth2Client
    callback_url = settings.REST_AUTH_GOOGLE_CALLBACK_URL


class UserView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    # permission_classes = [permissions.AllowAny]

    def get(self, request):
        # users = User.objects.all().order_by('-date_joined')
        # serializer = UserSerializer(users, many=True)
        # return Response(serializer.data)
        data = [
            {"name": "John", "age": 30},
            {"name": "Alex", "age": 29},
            {"name": "Lucas", "age": 33},
            {"name": "Emily", "age": 40},
            {"name": "Atom", "age": 66},
            {"name": "Atom", "age": 66},
        ]
        return Response(data)


class GroupView(APIView):
    # authentication_classes = [SessionAuthentication, TokenAuthentication]
    # permission_classes = [permissions.IsAuthenticated]
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        # group = Group.objects.all()
        # serializer = GroupSerializer(group, many=True)
        # return Response(serializer.data)

        data = [
            {
                "name": "Pizza da Mario 1",
                "cuisine": "Italian",
                "age": 7,
                "reviews": [
                    {"score": 4.5, "review": "The pizza was amazing!"},
                    {"score": 5.0, "review": "Very friendly staff, excellent service!"},
                ],
            },
            {
                "name": "Pizza da Mario 2",
                "cuisine": "Italian",
                "age": 8,
                "reviews": [
                    {"score": 4.5, "review": "The pizza was amazing!"},
                    {"score": 5.0, "review": "Very friendly staff, excellent service!"},
                ],
            },
            {
                "name": "Pizza da Mario 3",
                "cuisine": "Italian",
                "age": 9,
                "reviews": [
                    {"score": 4.5, "review": "The pizza was amazing!"},
                    {"score": 5.0, "review": "Very friendly staff, excellent service!"},
                ],
            },
            {
                "name": "Pizza da Mario 4",
                "cuisine": "Italian",
                "age": 10,
                "reviews": [
                    {"score": 4.5, "review": "The pizza was amazing!"},
                    {"score": 5.0, "review": "Very friendly staff, excellent service!"},
                ],
            },
            {
                "name": "Pizza da Mario 5",
                "cuisine": "Italian",
                "age": 11,
                "reviews": [
                    {"score": 4.5, "review": "The pizza was amazing!"},
                    {"score": 5.0, "review": "Very friendly staff, excellent service!"},
                ],
            },
        ]

        # data = [
        #     {"name": "John", "age": 30},
        #     {"name": "Alex", "age": 29},
        #     {"name": "Lucas", "age": 33},
        #     {"name": "Emily", "age": 40},
        #     {"name": "Atom", "age": 66},
        #     {"name": "Atom", "age": 66},
        # ]
        return Response(data)
