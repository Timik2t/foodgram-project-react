from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, RegexValidator
from django.db import models

from . import settings

User = get_user_model()


class Tag(models.Model):

    hex_validator = RegexValidator(
        regex='^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$',
        message=(
            'Введите валидный цветовой HEX-код!'
        )
    )

    name = models.CharField(
        max_length=settings.MAX_LENGTH_TAG_NAME,
        unique=True,
        verbose_name='Название'
    )
    slug = models.SlugField(
        unique=True,
        verbose_name='Идентификатор тега'
        )
    color = models.CharField(
        default='#49B64E',
        unique=True,
        max_length=7,
        validators=[hex_validator, ],
        verbose_name='Цветовой HEX-код',
        help_text='https://colorscheme.ru/html-colors.html'
        )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(
        max_length=settings.MAX_LENGTH_INGREDIENT_NAME,
        verbose_name='Название'
        )
    measurement_unit = models.CharField(
        max_length=settings.MAX_LENGTH_MEASUREMENT_UNIT,
        verbose_name='Единицы измерения'
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return self.name


class Recipe(models.Model):
    DISPLAY = (
        '{name}, '
        '{author}'
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='IngredientAmount',
        related_name='ingredients',
        verbose_name='Ингредиент'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор рецепта'
        )
    tags = models.ManyToManyField(
        Tag,
        related_name='tags',
        verbose_name='Тег'
    )
    name = models.CharField(
        max_length=settings.MAX_LENGTH_RECIPE_NAME,
        null=False,
        verbose_name='Название'
        )
    text = models.TextField(
        max_length=settings.MAX_LENGTH_RECIPE_TEXT,
        verbose_name='Описание рецепта'
        )
    image = models.ImageField(
        verbose_name='Картинка',
        upload_to='media/',
        blank=True
    )
    cooking_time_in_minutes = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(1)],
        verbose_name='Время приготовления (в минутах)',
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата публикации'
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ['-pub_date']

    def __str__(self):
        return self.DISPLAY.format(
            name=self.name,
            author=self.author
        )


class IngredientAmount(models.Model):
    DISPLAY = (
        '{ingredients}, '
        '{amount}'
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name='Ингредиент'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт'
        )
    amount = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(1)],
        verbose_name='Количество',
    )

    class Meta:
        verbose_name = 'Количество ингредиента для рецепта'
        constraints = [
            models.UniqueConstraint(
                name='recipe_ingredient_unique',
                fields=['recipe', 'ingredient'],
            ),
        ]


class BaseAddRecipeToList(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE
    )
    add_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата добавления'
    )

    def __str__(self):
        return self.name

    class Meta:
        abstract = True
        ordering = ('-add_date',)


class Favorite(BaseAddRecipeToList):

    class Meta(BaseAddRecipeToList.Meta):
        verbose_name = 'Избранное'
        constraints = [
            models.UniqueConstraint(
                name='favorite_unique',
                fields=['recipe', 'user'],
            ),
        ]


class ShoppingCart(BaseAddRecipeToList):

    class Meta(BaseAddRecipeToList.Meta):
        verbose_name = 'Список покупок'
