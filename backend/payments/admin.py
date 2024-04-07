from django.contrib import admin

from .models import Cashback, Payment, TariffKind

LIMIT_POSTS_PER_PAGE = 15


@admin.register(TariffKind)
class TariffKindAdmin(admin.ModelAdmin):
    """Администрирование тарифов."""

    list_display = (
        "name",
        "duration",
        "cost_per_month",
    )
    fields = (
        (
            "name",
            "duration",
        ),
        ("description",),
        (
            "cost_per_month",
            "cost_total",
        ),
    )
    search_fields = (
        "name",
        "duration",
    )
    list_filter = (
        "name",
        "duration",
    )
    list_editable = (
        "duration",
        "cost_per_month",
    )
    list_per_page = LIMIT_POSTS_PER_PAGE


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    """Администрирование платежей."""

    list_display = (
        "tariff_kind",
        "next_payment_date",
    )
    fields = (
        (
            "user",
            "tariff_kind",
            "service",
            "subscription",
        ),
        (
            "next_payment_date",
            "next_payment_amount",
        ),
    )
    search_fields = (
        "tariff_kind",
        "user",
    )
    list_filter = (
        "tariff_kind",
        "user",
    )
    list_per_page = LIMIT_POSTS_PER_PAGE


@admin.register(Cashback)
class SubscriptionAdmin(admin.ModelAdmin):
    """Администрирование кешбэка."""

    list_display = (
        "payment",
        "amount",
    )
    list_filter = ("payment",)
    search_fields = ("payment",)
    list_editable = ("amount",)
