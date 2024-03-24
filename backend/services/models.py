from typing import Optional
from django.core.validators import MaxValueValidator, MinValueValidator

from django.contrib.auth import get_user_model
# from django.core.validators import MinValueValidator
from django.db import models
from django.contrib.auth.models import User
from django.db.models import Exists, OuterRef
# from django.forms import MultiValueField, CharField, MultiWidget, TextInput
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.db.models import UniqueConstraint

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
    cost = models.PositiveIntegerField(
        'Стоимость подписки',
    )
    cashback = models.PositiveIntegerField(
        'Кэшбэк (в процентах)',
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
    # rating = какой тип поля? КАК ЕГО СЧИТАТЬ?

    objects = ServiceQuerySet.as_manager()

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'Сервис'
        verbose_name_plural = 'Сервисы'

    def __str__(self):
        return self.name

    @property
    def average_rating(self):
        ratings = Rating.objects.filter(service=self)
        total_ratings = sum([rating.stars for rating in ratings])
        if ratings:
            return total_ratings / len(ratings)
        return 0


# class AbstractSubscription(models.Model):
#     """Абстрактная модель атрибутов для подписок (и избр если будет). """

#     user = models.ForeignKey(
#         User,
#         on_delete=models.CASCADE,
#         verbose_name='Пользователь'
#     )
#     service = models.ForeignKey(
#         Service,
#         null=True,
#         default=None,
#         verbose_name='Сервис',
#         on_delete=models.CASCADE
#     )

#     class Meta:
#         constraints = [
#             models.UniqueConstraint(
#                 fields=('user', 'service'), name='unique_user_service_list'
#             )
#         ]
#         abstract = True


# class PhoneWidget(MultiWidget):
#     """Виджет для удобного заполнения телефонного номера. """

#     def __init__(self, code_length=3, num_length=7, attrs=None):
#         widgets = [
#             TextInput(
#                 attrs={'size': code_length, 'maxlength': code_length}
#             ),
#             TextInput(
#                 attrs={'size': num_length, 'maxlength': num_length}
#             )
#         ]
#         super(PhoneWidget, self).__init__(widgets, attrs)

#     def decompress(self, value):
#         if value:
#             return [value.code, value.number]
#         else:
#             return ['', '']


# class PhoneField(MultiValueField):
#     """Класс поля для ввода телефонного номера. """

#     def __init__(self, code_length, num_length, *args, **kwargs):
#         list_fields = [CharField(),
#                        CharField()]
#         super(PhoneField, self).__init__(
#             list_fields, widget=PhoneWidget(
#                 code_length, num_length
#             ), *args, **kwargs
#         )

#     def compress(self, values):
#         return '+7' + values[0] + values[1]


# class Subscription(AbstractSubscription):
#     """Модель подписок на сервисы. """

#     date_start = models.DateTimeField(
#         verbose_name='Дата активации',
#         auto_now_add=True,
#         db_index=True
#     )
#     date_stop = models.DateTimeField(
#         verbose_name='Действует до',
#         db_index=True
#     )
#     # поле телефон и виджет имеет смысл перенести в модель юзера
#     # в приложение users?
#     phone = PhoneField()
#     # поле цена уже должно быть в модели сервиса, надо ли повторять?
#     # cost=models.PositiveIntegerField(
#     #     'Стоимость подписки',
#     # )
#     tariff_description = models.TextField(verbose_name='Описание тарифа')
#     # cart_details = может это в приложение payments ?
#     # card_number = может это в приложение payments ?
#     # rules=
#     # status = активна/неактивна/в ожидании активации
#     # поле категория уже должно быть в модели сервиса, надо ли повторять?
#     # category =
#     # поле рейтинг уже должно быть в модели сервиса, надо ли повторять?
#     # rating =
#     # autorun = может это в приложение payments ?

#     class Meta:
#         default_related_name = 'subscription'
#         verbose_name = 'Объект подписки'
#         verbose_name_plural = 'Объекты подписки'

#     def __str__(self):
#         return f'Подписка {self.service} активна у {self.user}'


class Subscription(models.Model):
    """Модель подписки юзера на сервисы. """

    user = models.ForeignKey(
        User,
        related_name='subscriptions',
        on_delete=models.CASCADE
    )
    service = models.ForeignKey(
        Service,
        related_name='subscriptions',
        on_delete=models.CASCADE
    )
    subscribed_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=['user', 'service'], name='unique_subscription'
            )
        ]


@receiver(post_save, sender=Subscription)
def update_user_subscriptions_count(sender, instance, **kwargs):
    user = instance.user
    user.subscriptions_count = user.subscriptions.count()
    user.save()


class Rating(models.Model):
    """Модель рейтинга сервиса. """

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )
    service = models.ForeignKey(
        Service,
        on_delete=models.CASCADE
    )
    stars = models.IntegerField(
        choices=[(1, '1 star'),
                 (2, '2 stars'),
                 (3, '3 stars'),
                 (4, '4 stars'),
                 (5, '5 stars')]
    )
