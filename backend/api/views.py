from django.shortcuts import get_object_or_404
from recipes.models import Favorite, Ingredient, Recipe, ShoppingCart, Tag
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from users.models import Follow, User
from .pagination import LimitPageNumberPagination

from .permissions import IsAdminOrReadOnly, IsOwnerOrReadOnly
from .serializers import (CustomUserCreateSerializer, CustomUserSerializer,
                          FavoriteSerializer, FollowSerializer,
                          IngredientSerializer, RecipeListSerializer,
                          RecipeSerializer, ShoppingCartSerializer,
                          TagSerializer)


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = IngredientSerializer
    queryset = Ingredient.objects.all()
    permission_classes = (IsAdminOrReadOnly,)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = TagSerializer
    queryset = Tag.objects.all()
    permission_classes = (IsAdminOrReadOnly,)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    permission_classes = (IsOwnerOrReadOnly,)

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return RecipeListSerializer
        return RecipeSerializer

    @action(
        detail=True,
        methods=['post'],
        permission_classes=[IsAuthenticated]
    )
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

        return Response(
            {f'{recipe} Успешно удален из избраного!'},
            status=status.HTTP_204_NO_CONTENT
        )

    @action(
        detail=True,
        methods=['post'],
        permission_classes=[IsAuthenticated]
    )
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

        return Response(
            {f'{recipe} Успешно удален из списка покупок!'},
            status=status.HTTP_204_NO_CONTENT
        )

    @action(
        detail=False,
        methods=['get'],
        permission_classes=[IsAuthenticated]
    )
    def download_shopping_cart(self, request):
        pass


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    pagination_class = LimitPageNumberPagination

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return CustomUserSerializer
        return CustomUserCreateSerializer

    @action(
        detail=False,
        methods=['get'],
        permission_classes=[IsAuthenticated]
    )
    def me(self, request, pk=None):
        serializer = CustomUserSerializer(
            User.objects.filter(username=self.request.user),
            many=True
        )
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(
        detail=True,
        methods=['post'],
        permission_classes=[IsAuthenticated]
    )
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

        Follow.objects.filter(
            following=get_object_or_404(User, pk=pk),
            follower=self.request.user
        ).delete()
        serializer = FollowSerializer(
            Follow.objects.filter(following=following),
            many=True
        )
        return Response(serializer.data, status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, permission_classes=[IsAuthenticated])
    def subscriptions(self, request):
        serializer = FollowSerializer(
            Follow.objects.all(),
            many=True
        )
        return Response(serializer.data)
