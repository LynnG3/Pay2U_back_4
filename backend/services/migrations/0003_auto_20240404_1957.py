# Generated by Django 3.2.3 on 2024-04-04 16:57

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('services', '0002_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='subscription',
            options={'verbose_name': 'Подписка', 'verbose_name_plural': 'Подписки'},
        ),
        migrations.AddField(
            model_name='service',
            name='partners_link',
            field=models.TextField(default=str, validators=[django.core.validators.URLValidator()], verbose_name='сайт партнера'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='service',
            name='category',
            field=models.ForeignKey(blank=True, max_length=30, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='services', to='services.category', verbose_name='категория'),
        ),
    ]
