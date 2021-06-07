from rest_framework import viewsets, mixins, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from recipes.serializers import (
    TagSerializer,
    IngredientSerializer,
    RecipeSerializer,
    RecipeDetailSerializer,
    RecipeImageSerializer,
)
from core.models import Tag, Ingredient, Recipe


class BaseRecipeViewSet(
    viewsets.GenericViewSet, mixins.ListModelMixin, mixins.CreateModelMixin
):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user).order_by("-name")

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class TagViewSet(BaseRecipeViewSet):
    serializer_class = TagSerializer
    queryset = Tag.objects.all()


class IngredientViewSet(BaseRecipeViewSet):
    serializer_class = IngredientSerializer
    queryset = Ingredient.objects.all()


class RecipeViewSet(viewsets.ModelViewSet):
    serializer_class = RecipeSerializer
    queryset = Recipe.objects.all()
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user).order_by("-title")

    def get_serializer_class(self):
        if self.action == "retrieve":
            return RecipeDetailSerializer
        elif self.action == "upload_image":  # action will be the function name
            return RecipeImageSerializer

        return self.serializer_class

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    # Create a custom action with method POST
    # The detail=True means that the action will be a child of the detail url.
    # The url_path means that the 'upload-image' will be the url name
    # Url = "/api/recipe/<pk:id>/upload-image"
    @action(methods=["POST"], detail=True, url_path="upload-image")
    def upload_image(self, request, pk=None):
        recipe = self.get_object()  # Get the recipe object from the request

        # Get the serializer from the get_serializer_class function (line 48)
        serializer = self.get_serializer(recipe, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
