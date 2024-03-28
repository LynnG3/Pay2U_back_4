from django.db import models
from django.utils import timezone

from services.models import Service
# from users.models import CustomUser


class Tariff(models.Model):
    """Модель тарифа для подписки."""

    service = models.ForeignKey(
        Service,
        on_delete=models.CASCADE,
        verbose_name="Сервис",
    )
    name = models.CharField(
        max_length=50,
        verbose_name="Название сервиса"
    )
    # поле kind здесь нужно для реализации сортировки
    # по ценовой категрии тарифов от меньш к больш
    kind = models.ForeignKey(
        'TariffKind',
        on_delete=models.SET_NULL,
        null=True,
        verbose_name="Разновидность тарифа по длительности",
        related_name='tariffs'
    )
    description = models.TextField(
        verbose_name="Описание"
    )
    cashback = models.PositiveIntegerField(
        "Кэшбэк (в процентах)",
    )

    class Meta:
        ordering = ("-kind__cost_per_month",)
        verbose_name = "Тариф"

    def __str__(self):
        return self.name


class TariffKind(models.Model):
    """Модель разновидности тарифа по длительности."""

    tariff = models.ForeignKey(
        Tariff,
        on_delete=models.CASCADE,
        verbose_name="Тариф",
        related_name='tariff_kinds'
    )
    duration = models.PositiveIntegerField(
        "Длительность подписки в месяцах ",
    )
    cost_per_month = models.PositiveIntegerField(
        "Стоимость в месяц",
    )
    comment_1 = models.TextField(
        verbose_name="Инфо порядок оплаты"
    )
    # или лучше в сериализатор и рассчитывать по формуле
    # cost_per_month * duration ?
    comment_2 = models.PositiveIntegerField(
        verbose_name="Инфо стоимость далее"
    )

    class Meta:
        ordering = ("-duration",)
        verbose_name = "Разновидность тарифа"

    def save(self, *args, **kwargs):
        self.comment_2 = self.cost_per_month * self.duration
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
    CALLBACK_CHOICES = (
        ("accepted", "Принят"),
        ("denied", "Отклонен"),
    )
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
