from recepies.models import Ingredient, Recepie, Tag
from rest_framework import serializers


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        fields = ('name',)
        model = Ingredient


class RecepieSerializer(serializers.ModelSerializer):

    class Meta:
        fields = ('name',)
        model = Recepie


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        fields = ('name', 'slug')
        model = Tag
