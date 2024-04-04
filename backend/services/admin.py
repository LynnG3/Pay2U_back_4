from django.contrib import admin

from .models import Category, Rating, Service, Subscription

admin.site.empty_value_display = 'Не задано'
admin.site.site_header = 'Администрирование проекта "Pay2u"'
admin.site.site_title = 'Портал администраторов "Pay2u"'
admin.site.index_title = 'Добро пожаловать туда, где все под рукой'

LIMIT_POSTS_PER_PAGE = 15


class RatingInline(admin.TabularInline):
    model = Rating
    extra = 2


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """Администрирование категорий."""

    list_display = (
        "title",
        "image",
    )
    search_fields = ("title",)
    list_filter = ("title",)
    list_editable = ("image",)


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    """Администрирование сервисов."""

    inlines = (RatingInline,)
    list_display = (
        "name",
        "cost",
        "cashback_percentage",
    )
    fields = (
        (
            "name",
            "partners_link",
        ),
        ("text",),
        (
            "category",
            "cost",
            "cashback_percentage",
        ),
        (
            "image",
            "popular",
            "new",
        ),
    )
    search_fields = (
        "name",
        "category",
        "cashback_percentage",
    )
    list_filter = (
        "name",
        "category",
    )
    list_per_page = LIMIT_POSTS_PER_PAGE


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "service",
        "activation_status",
    )
    list_filter = (
        "activation_status",
        "service",
    )
    search_fields = ("user", "service", "activation_statis")
    list_editable = ("activation_status",)
