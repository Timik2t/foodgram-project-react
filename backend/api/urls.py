from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (FavoriteViewSet, FollowViewSet, IngredientViewSet,
                    RecipeViewSet, ShoppingCartViewSet, TagViewSet,
                    UserViewSet)

app_name = 'api'

router = DefaultRouter()
router.register(
    r'ingredients',
    IngredientViewSet,
    basename='ingredients'
)
router.register(
    r'recipes',
    RecipeViewSet,
    basename='recipes'
)
router.register(
    r'tags',
    TagViewSet,
    basename='tags'
)
router.register(
    r'favorite',
    FavoriteViewSet,
    basename='favorite'
)
router.register(
    r'shopping_cart',
    ShoppingCartViewSet,
    basename='shopping_cart'
)
router.register(
    r'users',
    UserViewSet,
    basename='users'
)
router.register(
    r'users',
    UserViewSet,
    basename='users'
)
router.register(
    r'subscriptions',
    FollowViewSet,
    basename='subscriptions'
)

urlpatterns = [
    path('', include(router.urls)),
]
