# Generated by Django 3.2.3 on 2024-03-24 20:53

import django.contrib.auth.models
import django.core.validators
import django.utils.timezone
from django.db import migrations, models

import users.validators


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='CustomUser',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('phone_number', models.CharField(max_length=12, unique=True, validators=[users.validators.validate_mobile], verbose_name='Номер телефона')),
                ('first_name', models.CharField(max_length=150, verbose_name='Имя')),
                ('last_name', models.CharField(max_length=150, verbose_name='Фамилия')),
                ('surname', models.CharField(max_length=150, verbose_name='Отчество')),
                ('username', models.CharField(max_length=150, unique=True, validators=[django.core.validators.RegexValidator(message='Имя пользователя содержит недопустимые символы.', regex='^[\\w.@+-]+$'), users.validators.validate_username], verbose_name='Уникальный юзернейм')),
                ('password', models.CharField(max_length=150, verbose_name='Пароль')),
                ('email', models.EmailField(max_length=254, unique=True, validators=[django.core.validators.EmailValidator()], verbose_name='Адрес электронной почты')),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.Group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.Permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': 'Пользователь',
                'verbose_name_plural': 'Пользователи',
                'ordering': ('username',),
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.AddConstraint(
            model_name='customuser',
            constraint=models.UniqueConstraint(fields=('username', 'email'), name='unique_user_with_email'),
        ),
    ]
