from rest_framework import viewsets

from recepies.models import Ingredient

from .serializers import (FavoriteSerializer, FollowSerializer,
                          IngredientSerializer, RecipeSerializer,
                          ShoppingCartSerializer, TagSerializer,
                          UserSerializer)


class IngredientViewSet(viewsets.ModelViewSet):
    serializer_class = IngredientSerializer
    queryset = Ingredient.objects.all()
    pass


class RecipeViewSet(viewsets.ModelViewSet):
    serializer_class = RecipeSerializer
    pass


class TagViewSet(viewsets.ModelViewSet):
    serializer_class = TagSerializer
    pass


class FavoriteViewSet(viewsets.ModelViewSet):
    serializer_class = FavoriteSerializer
    pass


class ShoppingCartViewSet(viewsets.ModelViewSet):
    serializer_class = ShoppingCartSerializer
    pass


class UserViewSet(viewsets.ModelViewSet):
    serializer_class = UserSerializer
    pass


class FollowViewSet(viewsets.ModelViewSet):
    serializer_class = FollowSerializer
    pass
