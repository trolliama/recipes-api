from rest_framework import viewsets, mixins, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

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
        assigned_only = bool(
            int(self.request.query_params.get("assigned_only", 0))
        )
        queryset = self.queryset
        if assigned_only:
            queryset = queryset.filter(recipe__isnull=False)

        return (
            queryset.filter(user=self.request.user)
            .order_by("-name")
            .distinct()
        )

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
    uploadImageParam = (  # Swagger upload-image endpoint parameter
        openapi.Parameter(
            name="image",
            in_=openapi.IN_FORM,
            description="Recipe image",
            required=True,
            type=openapi.TYPE_FILE,
        )
    )

    def get_queryset(self):
        # Will get the tags param from the json post request
        tags = self.request.query_params.get("tags")
        # Will get the ingredients param from the json post request
        ingredients = self.request.query_params.get("ingredients")
        queryset = self.queryset

        if tags:
            tags_id = map(int, tags.split(","))
            queryset = queryset.filter(tags__id__in=tags_id)
        if ingredients:
            ingredients_id = map(int, ingredients.split(","))
            queryset = queryset.filter(ingredients__id__in=ingredients_id)

        return queryset.filter(user=self.request.user).order_by("-title")

    def get_serializer_class(self):
        if self.action == "retrieve":
            return RecipeDetailSerializer
        elif self.action == "upload_image":  # action will be the function name
            return RecipeImageSerializer

        return self.serializer_class

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    # Schema for generate a form field to upload files
    @swagger_auto_schema(manual_parameters=[uploadImageParam])

    # Create a custom action with method POST
    # The detail=True means that the action will be a child of the detail url.
    # The url_path means that the 'upload-image' will be the url name
    # Url = "/api/recipe/<pk:id>/upload-image"
    @action(
        methods=["POST"],
        detail=True,
        url_path="upload-image",
        parser_classes=(
            MultiPartParser,
        ),  # Parser for the parameter on swagger ui
    )
    def upload_image(self, request, pk=None):
        recipe = self.get_object()  # Get the recipe object from the request

        # Get the serializer from the get_serializer_class function (line 48)
        serializer = self.get_serializer(recipe, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
