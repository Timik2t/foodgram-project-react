from django.shortcuts import get_object_or_404
from recepies.models import Ingredient, Tag
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from users.models import Follow, User

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
    queryset = Tag.objects.all()

    pass


class FavoriteViewSet(viewsets.ModelViewSet):
    serializer_class = FavoriteSerializer
    pass


class ShoppingCartViewSet(viewsets.ModelViewSet):
    serializer_class = ShoppingCartSerializer
    pass


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()

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
