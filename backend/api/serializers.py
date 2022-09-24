from recepies.models import Favorite, Ingredient, IngredientAmount, Recipe, ShoppingCart, Tag
from rest_framework import serializers
from users.models import Follow, User


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
    tags = TagSerializer(many=True)
    ingredients = IngredientAmountSerializer(
        source='ingredientamount_set',
        many=True,
        read_only=True,
    )

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


class FavoriteSerializer(serializers.ModelSerializer):

    class Meta:
        fields = ('id', 'name', 'image', 'cooking_time')
        model = Favorite


class ShoppingCartSerializer(serializers.ModelSerializer):

    class Meta:
        fields = ('id', 'name', 'image', 'cooking_time')
        model = ShoppingCart


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        fields = '__all__'
        model = User


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
