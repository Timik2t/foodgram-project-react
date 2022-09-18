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
        db_index=True
        )
    is_admin = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ('first_name', 'last_name', )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('username', )
