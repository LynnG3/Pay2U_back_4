import datetime
from random import choices
from typing import Optional

# from django.contrib.auth import get_user_model
# from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import Exists, OuterRef, UniqueConstraint
from django.db.models.signals import post_save

# from django.forms import MultiValueField, CharField, MultiWidget, TextInput
from django.dispatch import receiver
from users.models import CustomUser

# from django.core.validators import MaxValueValidator, MinValueValidator


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


class ServiceQuerySet(models.QuerySet):
    """Вспомогательная модель отображения
    отметки "вы подписаны" для списка сервисов.
    """

    def add_user_annotations(self, user_id: Optional[int]):
        return self.annotate(
            is_subscribed=Exists(
                Subscription.objects.filter(
                    user_id=user_id, service__pk=OuterRef("pk")
                )
            ),
        )


class Service(models.Model):
    """Модель сервиса."""

    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
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
    cashback = models.PositiveIntegerField(
        "Кэшбэк (в процентах)",
    )
    new = models.BooleanField(default=True)
    popular = models.BooleanField(default=False)
    # popular  - в сериализаторе или вью сделать счетчик подписчиков
    # функция если больше ??? меняется на True
    pub_date = models.DateTimeField(
        verbose_name="Дата добавления", auto_now_add=True, db_index=True
    )

    objects = ServiceQuerySet.as_manager()

    class Meta:
        ordering = ("-pub_date",)
        verbose_name = "Сервис"
        verbose_name_plural = "Сервисы"

    def __str__(self):
        return self.name

    def is_new(self):
        """Функция-счетчик для определения, является ли сервис новым."""
        today = datetime.date.today()
        delta_days = (today - self.pub_date.date()).days
        if delta_days <= 60:
            return True
        else:
            return False

    @property
    def new(self):
        return self.is_new()

    @property
    def average_rating(self):
        ratings = Rating.objects.filter(service=self)
        total_ratings = sum([rating.stars for rating in ratings])
        if ratings:
            return total_ratings / len(ratings)
        return 0


class Subscription(models.Model):
    """Модель подписки юзера на сервисы."""
    ACTIVATION_CHOICES = (
        (1, "Активирована"),
        (2, "недействительна"),
        (3, "ожидает активации"),
    )
    user = models.ForeignKey(
        CustomUser, related_name="subscriptions", on_delete=models.CASCADE
    )
    service = models.ForeignKey(
        Service, related_name="subscriptions", on_delete=models.CASCADE
    )
    payment_status = models.BooleanField(default=False)
    # но если это подписка - значит она уже оплачена? поле не нужно?
    activation_status = models.PositiveSmallIntegerField(
        "Статус активации подписки",
        choices=ACTIVATION_CHOICES,
    )
    # ожидает активации/активна/недействительна
    # или 3 булевых поля отдельно?
    # subscribed_date = models.DateField(auto_now_add=True)
    promo_code = models.CharField(max_length=12, blank=True, null=True)
    expiry_date = models.DateField(blank=True, null=True)

    class Meta:
        constraints = [
            UniqueConstraint(fields=["user", "service"],
                             name="unique_subscription")
        ]


@receiver(post_save, sender=Subscription)
def update_user_subscriptions_count(sender, instance, **kwargs):
    user = instance.user
    user.subscriptions_count = user.subscriptions.count()
    user.save()


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
