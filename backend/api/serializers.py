import base64

from django.core.files.base import ContentFile
from recipes.models import (Favorite, Ingredient, IngredientAmount, Recipe,
                            ShoppingCart, Tag)
from rest_framework import serializers
from users.models import Follow, User


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        fields = ('email', 'id', 'username', 'first_name', 'last_name',)
        model = User


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        fields = ('id', 'name', 'measurement_unit')
        model = Ingredient


class IngredientAmountSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(
        source='ingredient.id'
    )
    name = serializers.ReadOnlyField(
        source='ingredient.name'
    )
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        fields = ('id', 'name', 'measurement_unit', 'amount')
        model = IngredientAmount


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        fields = ('id', 'name', 'color', 'slug')
        model = Tag


class RecipeSerializer(serializers.ModelSerializer):
    ingredients = IngredientAmountSerializer(
        source='ingredientamount_set',
        many=True,
    )
    tags = TagSerializer(many=True)
    author = UserSerializer(read_only=True)
    image = Base64ImageField(required=False, allow_null=True)

    class Meta:
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'name',
            'image',
            'text',
            'cooking_time'
        )
        model = Recipe
        extra_kwargs = {
            'ingredients': {'required': True},
            'tags': {'required': True},
            'name': {'required': True},
            'text': {'required': True},
            'cooking_time': {'required': True},
        }


class BasePersonalListsSerializer(serializers.ModelSerializer):
    name = serializers.ReadOnlyField(
        source='recipe.name'
    )
    cooking_time = serializers.ReadOnlyField(
        source='recipe.cooking_time'
    )
    image = serializers.ReadOnlyField(
        source='recipe.image'
    )

    class Meta:
        fields = ('id', 'name', 'image', 'cooking_time')


class FavoriteSerializer(BasePersonalListsSerializer):

    class Meta(BasePersonalListsSerializer.Meta):
        model = Favorite


class ShoppingCartSerializer(BasePersonalListsSerializer):

    class Meta(BasePersonalListsSerializer.Meta):
        model = ShoppingCart


class FollowSerializer(serializers.ModelSerializer):
    following = serializers.SlugRelatedField(
        slug_field='username',
        queryset=User.objects.all()
    )

    follower = serializers.SlugRelatedField(
        slug_field='username',
        queryset=User.objects.all()
    )

    class Meta:
        fields = '__all__'
        model = Follow
