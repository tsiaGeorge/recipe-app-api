from rest_framework import authentication, mixins, permissions, status, \
    viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from core.models import Ingredient, Recipe, Tag
from .serializer import IngredientSerializer, RecipeDetailSerializer, \
    RecipeImageSerializer, RecipeSerializer, TagSerializer


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

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return RecipeDetailSerializer
        elif self.action == 'upload_image':
            return RecipeImageSerializer

        return self.serializer_class

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(methods=['POST'], detail=True, url_path='upload-image')
    def upload_image(self, request, pk=None):
        recipe = self.get_object()
        serializer = self.get_serializer(
            recipe,
            data=request.data
        )
        if serializer.is_valid():
            serializer.save()
            return Response(
                serializer.data,
                status=status.HTTP_200_OK
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )
