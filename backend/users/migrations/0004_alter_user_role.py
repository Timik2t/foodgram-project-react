# Generated by Django 4.1.1 on 2022-10-09 14:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_alter_user_username'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='role',
            field=models.TextField(choices=[('admin', 'admin'), ('user', 'user')], default='user', max_length=5, verbose_name='Роль'),
        ),
    ]