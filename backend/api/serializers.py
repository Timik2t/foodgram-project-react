from recepies.models import Favorite, Ingredient, Recipe, Tag, ShoppingCart
from rest_framework import serializers
from users.models import Follow, User


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        fields = ('id', 'name', 'measurement_unit')
        model = Ingredient


class RecipeSerializer(serializers.ModelSerializer):

    class Meta:
        fields = ('name',)
        model = Recipe


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        fields = ('id', 'name', 'color', 'slug')
        model = Tag


class FavoriteSerializer(serializers.ModelSerializer):

    class Meta:
        model = Favorite


class ShoppingCartSerializer(serializers.ModelSerializer):

    class Meta:
        model = ShoppingCart


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User


class FollowSerializer(serializers.ModelSerializer):

    class Meta:
        model = Follow
