from rest_framework import authentication, permissions, viewsets, mixins

from core.models import Tag, Ingredient
from .serializer import TagSerializer, IngredientSerializer


class TagViewSet(viewsets.GenericViewSet,
                 mixins.ListModelMixin,
                 mixins.CreateModelMixin):
    authentication_classes = (authentication.TokenAuthentication, )
    permission_classes = (permissions.IsAuthenticated, )
    serializer_class = TagSerializer
    queryset = Tag.objects.all()

    def get_queryset(self, *args, **kwargs):
        return self.queryset.filter(user=self.request.user).order_by('-name')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class IngredientViewSet(viewsets.GenericViewSet,
                 mixins.ListModelMixin,
                 mixins.CreateModelMixin):
    authentication_classes = (authentication.TokenAuthentication, )
    permission_classes = (permissions.IsAuthenticated, )
    serializer_class = IngredientSerializer
    queryset = Ingredient.objects.all()

    def get_queryset(self, *args, **kwargs):
        return self.queryset.filter(user=self.request.user).order_by('-name')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
