from django.db import models
from django.contrib.auth.models import AbstractUser
from . import settings


class User(AbstractUser):
    username = models.CharField(
        max_length=settings.MAX_LENGTH_USERNAME,
        unique=True,
        verbose_name='Логин'
        )
    first_name = models.CharField(
        verbose_name='Имя',
        max_length=settings.MAX_LENGTH_NAME
        )
    last_name = models.CharField(
        verbose_name='Фамилия',
        max_length=settings.MAX_LENGTH_SURNAME
        )
    email = models.EmailField(
        max_length=settings.MAX_LENGTH_EMAIL,
        unique=True,
        null=False,
        db_index=True
        )
    is_admin = models.BooleanField(default=False)

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'email']

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('username', )


class Follow(models.Model):
    following = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Автор'
    )
    follower = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Подписчик'
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        ordering = ('following', )
        constraints = [
            models.UniqueConstraint(
                name='follow_unique',
                fields=['following', 'follower'],
            ),
        ]
