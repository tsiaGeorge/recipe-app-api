from rest_framework import authentication, permissions, viewsets, mixins

from core.models import Tag, Ingredient, Recipe
from .serializer import TagSerializer, IngredientSerializer, RecipeSerializer


class BaseRecipeAttrs(viewsets.GenericViewSet,
                      mixins.CreateModelMixin,
                      mixins.ListModelMixin):

    authentication_classes = (authentication.TokenAuthentication, )
    permission_classes = (permissions.IsAuthenticated, )

    def get_queryset(self, *args, **kwargs):
        return self.queryset.filter(user=self.request.user).order_by('-name')

    def perform_create(self, serializer):
        return serializer.save(user=self.request.user)


class TagViewSet(BaseRecipeAttrs):

    serializer_class = TagSerializer
    queryset = Tag.objects.all()


class IngredientViewSet(BaseRecipeAttrs):

    serializer_class = IngredientSerializer
    queryset = Ingredient.objects.all()


class RecipeViewSet(viewsets.ModelViewSet):

    serializer_class = RecipeSerializer
    queryset = Recipe.objects.all()
    authentication_classes = (authentication.TokenAuthentication, )
    permission_classes = (permissions.IsAuthenticated, )

    def get_queryset(self, *args, **kwargs):
        return self.queryset.filter(user=self.request.user).order_by('-id')
