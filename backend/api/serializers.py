from djoser.serializers import UserCreateSerializer, UserSerializer
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from recipes.models import (Favorite, Ingredient, IngredientAmount, Recipe,
                            ShoppingCart, Tag)
from users.models import Follow, User


class CustomUserSerializer(UserSerializer):

    is_subscribed = serializers.SerializerMethodField(read_only=True)

    class Meta:
        fields = (
            'email', 'id', 'username',
            'first_name', 'last_name', 'is_subscribed'
        )
        model = User

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return Follow.objects.filter(
            follower=obj,
            following=request.user
        ).exists()


class CustomUserCreateSerializer(UserCreateSerializer):

    class Meta:
        fields = (
            'email', 'id', 'username',
            'first_name', 'last_name', 'password'
        )
        model = User


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        fields = ('id', 'name', 'color', 'slug')
        model = Tag


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        fields = ('id', 'name', 'measurement_unit')
        model = Ingredient


class IngredientAmountSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())
    name = serializers.ReadOnlyField(
        source='ingredient.name',
        read_only=True
    )
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit',
        read_only=True
    )
    amount = serializers.IntegerField()

    class Meta:
        fields = ('id', 'name', 'measurement_unit', 'amount')
        model = IngredientAmount


TAGS_AMOUNT = 'Выберите хотя бы один тэг!'
UNIQ_TAGS = 'Тэги должны быть уникальными!'
MIN_COOKING_TIME = 'Время приготовления должно быть > 0!'
INGREDIENTS_AMOUNT = 'Количество ингредиента должно быть больше нуля!'
UNIQ_INGREDIENTS = 'Ингредиенты должны быть уникальными!'


class RecipeSerializer(serializers.ModelSerializer):
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True
    )
    ingredients = IngredientAmountSerializer(many=True)
    author = CustomUserSerializer(read_only=True)
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'id', 'author', 'ingredients', 'tags', 'image',
            'name', 'text', 'cooking_time'
        )
        extra_kwargs = {
            'cooking_time': {'required': True},
            'image': {'required': True}
        }

    def validate(self, data):
        ingredients = data['ingredients']
        ingredients_id = [ingredient['id'] for ingredient in ingredients]
        if len(set(ingredients_id)) != len(ingredients_id):
            raise serializers.ValidationError({
                'ingredients': UNIQ_INGREDIENTS
            })

        amounts = [ingredient['amount'] for ingredient in ingredients]
        for amount in amounts:
            if int(amount) <= 0:
                raise serializers.ValidationError({
                    'amount': INGREDIENTS_AMOUNT
                })

        tags = data['tags']
        if not tags:
            raise serializers.ValidationError({
                'tags': TAGS_AMOUNT
            })

        if len(set(tags)) != len(tags):
            raise serializers.ValidationError({
                'tags': UNIQ_TAGS
            })

        cooking_time = data['cooking_time']
        if int(cooking_time) <= 0:
            raise serializers.ValidationError({
                'cooking_time': MIN_COOKING_TIME
            })
        return data

    @staticmethod
    def create_ingredients(ingredients, recipe):
        IngredientAmount.objects.bulk_create(
            IngredientAmount(
                recipe=recipe,
                ingredient=ingredient['name'],
                amount=ingredient['amount']
            ) for ingredient in ingredients
        )

    @staticmethod
    def create_tags(tags, recipe):
        for tag in tags:
            recipe.tags.add(tag)

    def create(self, validated_data):
        author = self.context.get('request').user
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(author=author, **validated_data)
        self.create_tags(tags, recipe)
        self.create_ingredients(ingredients, recipe)
        return recipe

    def to_representation(self, instance):
        request = self.context.get('request')
        context = {'request': request}
        return RecipeListSerializer(instance, context=context).data

    def update(self, instance, validated_data):
        instance.tags.clear()
        IngredientAmount.objects.filter(recipe=instance).delete()
        self.create_tags(validated_data.pop('tags'), instance)
        self.create_ingredients(validated_data.pop('ingredients'), instance)
        return super().update(instance, validated_data)


class RecipeListSerializer(serializers.ModelSerializer):
    ingredients = IngredientAmountSerializer(
        source='ingredientamount_set',
        many=True,
    )
    tags = TagSerializer(many=True)
    author = CustomUserSerializer()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author', 'ingredients', 'is_favorited',
            'is_in_shopping_cart', 'image', 'name',
            'image', 'text', 'cooking_time'
        )
        read_only_fields = '__all__',

    def get_is_favorited(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return Favorite.objects.filter(
            recipe=obj,
            user=user
        ).exists()

    def get_is_in_shopping_cart(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return ShoppingCart.objects.filter(
            recipe=obj,
            user=user
        ).exists()


class ShortRecipeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


SELF_FOLLOW = 'Нельзя подписаться на самого себя'
DOUBLE_FOLLOW = 'Подписка уже существует'


class FollowSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='following.id')
    email = serializers.ReadOnlyField(source='following.email')
    username = serializers.ReadOnlyField(source='following.username')
    first_name = serializers.ReadOnlyField(source='following.first_name')
    last_name = serializers.ReadOnlyField(source='following.last_name')
    is_subscribed = serializers.SerializerMethodField(read_only=True)
    recipes = serializers.SerializerMethodField(read_only=True)
    recipes_count = serializers.SerializerMethodField(read_only=True)

    class Meta:
        fields = (
            'id', 'email', 'username', 'first_name',
            'last_name', 'is_subscribed', 'recipes', 'recipes_count'
        )
        model = Follow
        validators = [
            UniqueTogetherValidator(
                queryset=Follow.objects.all(),
                fields=['follower', 'following'],
                message=DOUBLE_FOLLOW
            )
        ]

    def validate_following(self, value):
        if self.context['request'].user == value:
            raise serializers.ValidationError(SELF_FOLLOW)
        return value

    def get_recipes(self, obj):
        request = self.context.get('request')
        limit_recipes = request.query_params.get('recipes_limit')
        recipe = Recipe.objects.filter(author=obj.following)
        if limit_recipes is not None:
            recipes = recipe.all()[:(int(limit_recipes))]
        else:
            recipes = recipe.all()
        context = {'request': request}
        return ShortRecipeSerializer(
            recipes,
            many=True,
            context=context).data

    def get_is_subscribed(self, obj):
        following = obj.following
        if not following:
            return False
        return Follow.objects.filter(
            following=obj.follower,
            follower=following
        ).exists()

    @staticmethod
    def get_recipes_count(obj):
        return Recipe.objects.filter(author=obj.following).count()
