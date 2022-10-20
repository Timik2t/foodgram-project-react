from django.urls import include, path, re_path
from rest_framework.routers import DefaultRouter

from .views import IngredientViewSet, RecipeViewSet, TagViewSet, UserViewSet

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
    r'ingredients',
    IngredientViewSet,
    basename='ingredients'
)

urlpatterns = [
    re_path(r'^auth/', include('djoser.urls.authtoken')),
    path('', include(router.urls)),
    path('', include('djoser.urls')),
]
