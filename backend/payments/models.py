from django.contrib.auth import get_user_model
from django.db import models
from services.models import Service

User = get_user_model()

CALLBACK_CHOICES = (
    ("accepted", "Принят"),
    ("denied", "Отклонен"),
)

DISCOUNT = 0.75

DURATION_CHOICES = (
    (1, '1 месяц'),
    (3, '3 месяца'),
    (6, '6 месяцев'),
    (12, '12 месяцев')
)

CASHBACK_CHOICES = ()


class TariffKind(models.Model):
    """Модель разновидности тарифа по длительности."""

    # тип поля service здесь многие ко многим -
    # тк например 2 сервиса (кинопоиск + амедиатека) -
    # 4 варианта по длительности
    service = models.ManyToManyField(
        Service,
        verbose_name="Сервис",
        related_name="tariffs_services",
    )
    name = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        default=None,
        verbose_name="Название тарифа",
    )
    duration = models.PositiveIntegerField(
        choices=DURATION_CHOICES,
        verbose_name="Длительность подписки в месяцах ",
        editable=True,
    )
    cost_per_month = models.IntegerField(
        default=199,
        verbose_name="Стоимость в месяц",
        editable=True,
    )
    cost_total = models.IntegerField(
        default=199,
        verbose_name="Стоимость за период",
        editable=True,
    )
    description = models.TextField(
        null=True,
        blank=True,
        verbose_name="Описание тарифа",
        editable=True,
    )
    cashback = models.PositiveIntegerField(
        default=5,
        verbose_name="Кэшбэк (в процентах)",
        editable=True,
    )
    comment_1 = models.TextField(
        null=True,
        blank=True,
        verbose_name="Частота оплаты",
        editable=True,
    )
    comment_2 = models.TextField(
        null=True,
        blank=True,
        verbose_name="Стоимость далее",
        editable=True,
    )

    class Meta:
        ordering = ("-cost_per_month",)
        verbose_name = "Тариф"
        verbose_name_plural = "Тарифы"

    def calculate_cost_per_month(self, duration):
        """Вычисляет цену за месяц в завис. от длительности подписки."""
        return int(self.cost_per_month * DISCOUNT ** (duration - 1))

    def save(self, *args, **kwargs):
        """Сохраняет итоговые значения в завсисмости
        от вычисленной цены за месяц. Выводит комментарии об условиях тарифа.
        """
        self.cost_per_month = self.calculate_cost_per_month(self.duration)
        self.cost_total = self.cost_per_month * self.duration
        self.comment_1 = (
            f'Далее {self.cost_total} при оплате раз в {self.duration} мес.'
        )
        self.comment_2 = f'Далее {self.cost_total}'
        super(TariffKind, self).save(*args, **kwargs)

    def __str__(self):
        return self.duration


class Payment(models.Model):
    """Модель оплаты подписки.
    Будет использвана также для истории платежей.
    """

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="Плательщик",
        related_name="payment_users",
    )
    service = models.ForeignKey(
        Service,
        on_delete=models.CASCADE,
        verbose_name="Сервис",
        related_name="payment_services",
    )
    tariff_kind = models.ForeignKey(
        TariffKind,
        on_delete=models.CASCADE,
        verbose_name="Выбранный тариф",
        related_name="payment_tariffs",
    )
    total = models.PositiveIntegerField(
        verbose_name="Общая стоимость",
    )
    accept_rules = models.BooleanField(
        default=False,
        verbose_name="Согласие с правилами",
    )
    # заглушка для ответа банка
    callback = models.CharField(
        max_length=10,
        choices=CALLBACK_CHOICES,
        verbose_name="Ответ от банка",
    )
    payment_date = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        verbose_name="Дата оплаты",
    )
    next_payment_date = models.DateField()
    next_payment_amount = models.PositiveIntegerField()

    class Meta:
        ordering = ["-payment_date"]
        verbose_name = "Платеж"
        verbose_name_plural = "Платежи"

    def save(self, *args, **kwargs):
        self.total = self.tariff_kind.comment_2
        super(Payment, self).save(*args, **kwargs)

    def __str__(self):
        return f"{self.service} - {self.total}"


class Cashback(models.Model):
    """Модель кешбэка."""

    payment = models.OneToOneField(
        Payment,
        on_delete=models.CASCADE,
        verbose_name="Платеж",
        related_name="cashbacks",
    )
    amount = models.DecimalField(
        "Сумма кешбэка",
        max_digits=8,
        decimal_places=2,
    )

    class Meta:
        verbose_name = "Кешбэк"
        verbose_name_plural = "Кешбэк"
