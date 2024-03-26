from django.contrib import admin

from .models import Category, Service


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """Администрирование категорий."""

    list_display = ("title",)
    search_fields = ("title",)
    list_filter = ("title",)


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    """Администрирование сервисов."""

    list_display = (
        "name",
        "category",
        "text",
        "cost",
        "cashback",
        "new",
        "popular",
        "pub_date",
    )
    search_fields = ("name",)
    list_filter = ("name",)
