from django.db import models
from django.utils import timezone
from services.models import Service

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


class TariffKind(models.Model):
    """Модель разновидности тарифа по длительности."""

    # тип поля service здесь многие ко многим -
    # тк например 2 сервиса (кинопоиск + амедиатека) -
    # 4 варианта по длительности
    service = models.ManyToManyField(
        Service,
        verbose_name="Сервис",
    )
    name = models.CharField(
        max_length=50,
        null=True,
        default=None,
        verbose_name="Название тарифа"
    )
    duration = models.PositiveIntegerField(
        verbose_name="Длительность подписки в месяцах ",
        choices=DURATION_CHOICES,
    )
    cost_per_month = models.IntegerField(
        verbose_name="Стоимость в месяц",
        default=199
    )
    cost_total = models.IntegerField(
        verbose_name="Стоимость за период",
        default=199
    )
    description = models.TextField(
        verbose_name="Описание тарифа",
        null=True
    )
    cashback = models.PositiveIntegerField(
        "Кэшбэк (в процентах)",
        default=5
    )
    comment_1 = models.TextField(
        verbose_name="Частота оплаты",
        null=True
    )
    comment_2 = models.TextField(
        verbose_name="Стоимость далее",
        null=True
    )

    class Meta:
        ordering = ("-cost_per_month",)
        verbose_name = "Разновидность тарифа"

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

    service = models.ForeignKey(
        Service,
        on_delete=models.CASCADE,
        verbose_name="Сервис",
    )
    tariff_kind = models.ForeignKey(
        TariffKind,
        on_delete=models.CASCADE,
        verbose_name="Выбранный тариф",
    )
    total = models.PositiveIntegerField(
        verbose_name="Общая стоимость"
    )
    phone_number = models.CharField(
        verbose_name="Номер телефона",
        max_length=11,
        blank=True,
    )
    # card = способ оплаты
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
        verbose_name="Дата оплаты",
        auto_now_add=True, db_index=True
    )

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

    payment = models.ForeignKey(
        Payment,
        on_delete=models.CASCADE,
        verbose_name="Платеж",
        related_name='cashbacks'
    )

    class Meta:
        verbose_name = "Кешбэк"

    @classmethod
    def calculate_total_cashback_rub(cls, user):
        start_date = timezone.now().replace(day=1) - timezone.timedelta(days=1)
        end_date = start_date.replace(day=1)
        user_payments = Payment.objects.filter(
            service__subscriptions__user=user,
            payment_date__range=(end_date, start_date)
        )
        total_cashback_rub = sum(
            payment.total * (payment.tariff_kind.tariff.cashback / 100)
            for payment in user_payments
        )
        return total_cashback_rub
