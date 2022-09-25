from django.shortcuts import get_object_or_404
from recipes.models import Favorite, Ingredient, Recipe, ShoppingCart, Tag
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from users.models import Follow, User

from .serializers import (FavoriteSerializer, FollowSerializer,
                          IngredientSerializer, RecipeListSerializer,
                          RecipeSerializer, ShoppingCartSerializer,
                          TagSerializer, UserSerializer)


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = IngredientSerializer
    queryset = Ingredient.objects.all()


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = TagSerializer
    queryset = Tag.objects.all()


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return RecipeListSerializer
        return RecipeSerializer

    @action(detail=True, methods=['post'])
    def favorite(self, request, pk=None):
        Favorite.objects.create(
            recipe=get_object_or_404(Recipe, pk=pk),
            user=request.user
        )
        serializer = FavoriteSerializer(
            Favorite.objects.all(),
            many=True
        )
        return Response(serializer.data)

    @favorite.mapping.delete
    def del_favorite(self, request, pk=None):
        recipe = get_object_or_404(Recipe, pk=pk)

        if not Favorite.objects.filter(
            recipe=recipe,
            user=request.user
        ).exists():
            return Response({
                'errors': f'{recipe} не находится в вашем избранном!'
            }, status=status.HTTP_400_BAD_REQUEST)

        Favorite.objects.filter(
            recipe=recipe,
            user=request.user
        ).delete()

        return Response({
                f'{recipe} Успешно удален из избраного!'
            }, status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['post'])
    def shopping_cart(self, request, pk=None):
        ShoppingCart.objects.create(
            recipe=get_object_or_404(Recipe, pk=pk),
            user=request.user
        )
        serializer = ShoppingCartSerializer(
            ShoppingCart.objects.all(),
            many=True
        )
        return Response(serializer.data)

    @shopping_cart.mapping.delete
    def del_shopping_cart(self, request, pk=None):
        recipe = get_object_or_404(Recipe, pk=pk)

        if not ShoppingCart.objects.filter(
            recipe=recipe,
            user=request.user
        ).exists():
            return Response({
                'errors': f'{recipe} не находится в вашем списке покупок!'
            }, status=status.HTTP_400_BAD_REQUEST)

        ShoppingCart.objects.filter(
            recipe=recipe,
            user=request.user
        ).delete()

        return Response({
                f'{recipe} Успешно удален из списка покупок!'
            }, status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['get'])
    def download_shopping_cart(self, request):
        pass


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    @action(detail=True, methods=['post'])
    def subscribe(self, request, pk=None):
        following = get_object_or_404(User, pk=pk)

        if request.user == following:
            return Response({
                'errors': 'Вы не можете подписываться на самого себя'
            }, status=status.HTTP_400_BAD_REQUEST)

        Follow.objects.create(
            following=get_object_or_404(User, pk=pk),
            follower=self.request.user
        )
        serializer = FollowSerializer(
            Follow.objects.filter(following=following),
            many=True
        )
        return Response(serializer.data)

    @subscribe.mapping.delete
    def del_subscribe(self, request, pk=None):
        following = get_object_or_404(User, pk=pk)

        if not Follow.objects.filter(
            following=get_object_or_404(User, pk=pk),
            follower=self.request.user
        ).exists():
            return Response({
                'errors': f'Вы не подписанны на автора {following}'
            }, status=status.HTTP_400_BAD_REQUEST)

        Follow.objects.delete(
            following=get_object_or_404(User, pk=pk),
            follower=self.request.user
        )
        serializer = FollowSerializer(
            Follow.objects.filter(following=following),
            many=True
        )
        return Response(serializer.data)

    @action(detail=False)
    def subscriptions(self, request):
        serializer = FollowSerializer(
            Follow.objects.all(),
            many=True
        )
        return Response(serializer.data)
