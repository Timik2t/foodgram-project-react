from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (FavoriteViewSet, IngredientViewSet,
                    RecipeViewSet, TagViewSet,
                    UserViewSet)

app_name = 'api'

router = DefaultRouter()
router.register(
    r'users',
    UserViewSet,
    basename='users'
)
router.register(
    r'tags',
    TagViewSet,
    basename='tags'
)
router.register(
    r'recipes',
    RecipeViewSet,
    basename='recipes'
)
router.register(
    r'favorite',
    FavoriteViewSet,
    basename='favorite'
)
router.register(
    r'ingredients',
    IngredientViewSet,
    basename='ingredients'
)

urlpatterns = [
    path('', include(router.urls)),
]
