import datetime

from django.contrib.auth import get_user_model
from django.core.validators import URLValidator
from django.db import models
from django.db.models import UniqueConstraint
from django.db.models.signals import post_save

# from django.forms import MultiValueField, CharField, MultiWidget, TextInput
from django.dispatch import receiver
from users.models import CustomUser

# from random import choices
# from typing import Optional


# from django.core.validators import MaxValueValidator, MinValueValidator


# TariffKind = apps.get_model('services', 'TariffKind')
User = get_user_model()


class Category(models.Model):
    """Модель тематической категории сервиса."""

    title = models.CharField("Заголовок", max_length=30)
    image = models.ImageField(
        "Ссылка на изображение",
        upload_to="categories/images/",
        null=True,
        default=None,
    )

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"
        ordering = ("title",)

    def __str__(self):
        return self.title


class Service(models.Model):
    """Модель сервиса."""

    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        related_name="services",
        verbose_name="категория",
        max_length=30,
        blank=True,
        null=True,
    )
    name = models.CharField(
        max_length=50,
        verbose_name="Название сервиса"
    )
    image = models.ImageField(
        "Ссылка на изображение",
        upload_to="services/images/",
        null=True,
        default=None,
    )
    text = models.TextField(
        "Описание",
    )
    cost = models.PositiveIntegerField(
        "Стоимость подписки",
    )
    cashback_percentage = models.PositiveIntegerField(
        "Кэшбэк (в процентах)",
    )
    new = models.BooleanField(default=True)
    popular = models.BooleanField(default=False)
    pub_date = models.DateTimeField(
        verbose_name="Дата добавления", auto_now_add=True, db_index=True
    )
    partners_link = models.TextField(
        verbose_name="сайт партнера",
        validators=[
            URLValidator(),
        ],
    )

    class Meta:
        ordering = ("-pub_date",)
        verbose_name = "Сервис"
        verbose_name_plural = "Сервисы"

    def __str__(self):
        return self.name


class Subscription(models.Model):
    """Модель подписки юзера на сервисы."""
    ACTIVATION_CHOICES = (
        (1, "Активирована"),
        (2, "недействительна"),
        (3, "ожидает активации"),
    )
    user = models.ForeignKey(
        User, related_name="subscriptions", on_delete=models.CASCADE
    )
    service = models.ForeignKey(
        Service, related_name="subscriptions", on_delete=models.CASCADE
    )
    # payment_status = models.BooleanField(default=False)
    # # но если это подписка оплачена, поле payment_status не нужно?
    # если успеем хорошо бы менять автоматически activation_status после оплаты
    # етогда по умолчанию ????
    autopayment = models.BooleanField(
        default=False,
        verbose_name="автоплатеж",
    )

    activation_status = models.PositiveSmallIntegerField(
        "Статус активации подписки",
        choices=ACTIVATION_CHOICES,
    )
    promo_code = models.CharField(max_length=12, blank=True, null=True)
    expiry_date = models.DateField(blank=True, null=True)
    # пробный период
    trial = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Подписка"
        verbose_name_plural = "Подписки"
        constraints = [
            UniqueConstraint(fields=["user", "service"],
                             name="unique_subscription")
        ]

"""
@receiver(post_save, sender=Subscription)
def update_user_subscriptions_count(sender, instance, **kwargs):
    user = instance.user
    user.subscriptions_count = user.subscriptions.count()
    if user.subscriptions_count >= 50:
        services = Service.objects.filter(subscriptions__user=user)
        for service in services:
            service.popular = True
            service.save()
    user.save()"""


class Rating(models.Model):
    """Модель рейтинга сервиса."""

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    stars = models.IntegerField(
        choices=[
            (1, "1 star"),
            (2, "2 stars"),
            (3, "3 stars"),
            (4, "4 stars"),
            (5, "5 stars"),
        ]
    )
