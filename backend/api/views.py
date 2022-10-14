import datetime

from django.shortcuts import HttpResponse, get_object_or_404
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .filters import AuthorTagFilter, IngredientSearchFilter
from .pagination import LimitPageNumberPagination
from .permissions import IsAdminOrReadOnly, IsOwnerOrReadOnly
from .serializers import (CustomUserCreateSerializer, CustomUserSerializer,
                          FavoriteSerializer, FollowSerializer,
                          IngredientSerializer, RecipeListSerializer,
                          RecipeSerializer, ShoppingCartSerializer,
                          TagSerializer)
from recipes.models import (Favorite, Ingredient, IngredientAmount, Recipe,
                            ShoppingCart, Tag)
from users.models import Follow, User


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = IngredientSerializer
    queryset = Ingredient.objects.all()
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (IngredientSearchFilter,)
    search_fields = ('^name',)
    pagination_class = None


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = TagSerializer
    queryset = Tag.objects.all()
    permission_classes = (IsAdminOrReadOnly,)
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    permission_classes = (IsOwnerOrReadOnly,)
    filter_class = AuthorTagFilter
    pagination_class = LimitPageNumberPagination

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
        return Response(serializer.data, status=status.HTTP_201_CREATED)

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
        return Response(serializer.data, status=status.HTTP_201_CREATED)

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
        shopping_list = {}
        ingredients = IngredientAmount.objects.select_related(
            'recipe', 'ingredient'
        )
        ingredients = ingredients.filter(
            recipe__shopping_carts__user=request.user
        )
        for ingredient in ingredients:
            amount = ingredient.amount
            name = ingredient.ingredient.name
            measurement_unit = ingredient.ingredient.measurement_unit
            if name not in shopping_list:
                shopping_list[name] = {
                    'measurement_unit': measurement_unit,
                    'amount': amount
                }
            else:
                shopping_list[name]['amount'] += amount
        main_list = (
            [f"* {item}: {value['amount']}"
             f" {value['measurement_unit']};\n"
             for item, value in shopping_list.items()]
        )
        main_list.append(
            f'\n FoodGram, connecting people (｡◕‿◕｡)'
            f'\n {datetime.date.today().year}'
        )
        response = HttpResponse(main_list, 'Content-Type: text/plain')
        response['Content-Disposition'] = (
            'attachment; filename="ShoppingList.txt"')
        return response


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
