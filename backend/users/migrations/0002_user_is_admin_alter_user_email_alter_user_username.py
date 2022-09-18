# Generated by Django 4.1.1 on 2022-09-18 14:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='is_admin',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='user',
            name='email',
            field=models.EmailField(db_index=True, max_length=250, unique=True),
        ),
        migrations.AlterField(
            model_name='user',
            name='username',
            field=models.CharField(max_length=50, unique=True, verbose_name='Логин'),
        ),
    ]
