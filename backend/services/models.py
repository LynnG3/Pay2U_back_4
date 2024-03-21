from typing import Optional

from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import Exists, OuterRef

# from users.models import CustomUser

User = get_user_model()

SHOW_SYMBOLS = 30


class Category(models.Model):
    """Модель тематической категории сервиса. """

    title = models.CharField('Заголовок', max_length=30)
    slug = models.SlugField('Слаг', unique=True)
    # description = models.TextField('Описание')

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'категории'
        ordering = ('title',)

    def __str__(self):
        return self.title[:SHOW_SYMBOLS]


class ServiceQuerySet(models.QuerySet):
    """Вспомогательная модель отображения
    отметки "вы подписаны" для списка сервисов.
    """

    def add_user_annotations(self, user_id: Optional[int]):
        return self.annotate(
            is_subscribed=Exists(
                Subscription.objects.filter(
                    user_id=user_id, service__pk=OuterRef('pk')
                )
            ),
        )


class Service(models.Model):
    """Модель сервиса. """

    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        verbose_name='категория',
        max_length=30,
        blank=True,
        null=True
    )
    name = models.CharField(
        max_length=50,
        verbose_name='Название сервиса'
    )
    image = models.ImageField(
        "Ссылка на изображение",
        upload_to="services/images/",
        null=True,
        default=None
    )
    text = models.TextField(verbose_name='Текст')
    cashback = models.PositiveIntegerField(
        'Кэшбэк (в процентах)',
        # validators=[
        #     MinValueValidator(
        #         1,
        #         'Кэшбэк не может быть меньше 1 процента'
        #     )
        # ],
    )
    new = models.BooleanField(default=True)
    # new  - в сериализаторе или вью сделать счетчик дней
    # функция если больше 60 меняется на False
    popular = models.BooleanField(default=False)
    # popular  - в сериализаторе или вью сделать счетчик звезд
    # функция если больше ??? меняется на True
    pub_date = models.DateTimeField(
        verbose_name='Дата добавления',
        auto_now_add=True,
        db_index=True
    )

    objects = ServiceQuerySet.as_manager()

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'Сервис'
        verbose_name_plural = 'Сервисы'

    def __str__(self):
        return self.name


class AbstractSubscription(models.Model):
    """Абстрактная модель атрибутов для подписок (и избранного если будет). """

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь'
    )
    service = models.ForeignKey(
        Service,
        null=True,
        default=None,
        verbose_name='Сервис',
        on_delete=models.CASCADE
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=('user', 'service'), name='unique_user_service_list'
            )
        ]
        abstract = True


class Subscription(AbstractSubscription):
    """Модель подписок на сервисы. """

    class Meta:
        default_related_name = 'subscription'
        verbose_name = 'Объект подписки'
        verbose_name_plural = 'Объекты подписки'

    def __str__(self):
        return f'Подписка {self.service} активна у {self.user}'
