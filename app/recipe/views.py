from rest_framework import authentication, permissions
from rest_framework.viewsets import ModelViewSet

from core.models import Tag
from .serializer import TagSerializer


class TagViewSet(ModelViewSet):
    authentication_classes = (authentication.TokenAuthentication, )
    permission_classes = (permissions.IsAuthenticated, )
    serializer_class = TagSerializer
    queryset = Tag.objects.all()

    def get_queryset(self, *args, **kwargs):
        return self.queryset.filter(user=self.request.user).order_by('-name')
