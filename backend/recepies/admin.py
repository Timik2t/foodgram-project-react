from django.contrib import admin

from .models import Recepie, Ingredient, Tag


@admin.register(Recepie)
class RecepieAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'author',
    )
    search_fields = (
        'name',
        'author',
        'tags'
        )
    empty_value_display = '-пусто-'


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'slug',
        'color',
    )
    prepopulated_fields = {"slug": ("name",)}
    list_editable = ('color',)
    search_fields = ('name',)
    empty_value_display = '-пусто-'


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'name',
        'measurement_unit',
    )
    list_editable = ('name',)
    list_filter = ('name',)
    empty_value_display = '-пусто-'
