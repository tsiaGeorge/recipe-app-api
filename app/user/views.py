from rest_framework import generics, authentication, permissions
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.settings import api_settings

from .serializers import UserSerializer, AuthTokenSerializer


class CreateUserView(generics.CreateAPIView):
    serializer_class = UserSerializer


class CreateTokenView(ObtainAuthToken):
    serializer_class = AuthTokenSerializer
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES


class RetrieveUpdateUserView(generics.RetrieveUpdateAPIView):
    authentication_classes = (authentication.TokenAuthentication, )
    permission_classes = (permissions.IsAuthenticated, )
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user
