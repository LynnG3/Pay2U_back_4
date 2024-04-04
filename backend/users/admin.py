from django.contrib import admin
from django.contrib.auth import get_user_model
from services.models import Subscription

User = get_user_model()
LIMIT_POSTS_PER_PAGE = 15


class SubscriptionInline(admin.TabularInline):
    'Таблица с подписками пользователей. '

    model = Subscription
    fields = [
        'service',
        'tariff',
        'activation_status',
    ]


@admin.register(User)
class UserAdmin(admin.ModelAdmin):

    inlines = [SubscriptionInline]
    list_display = (
        "username",
        "first_name",
        "last_name",
        "surname",
        "email",
        "phone_number",
        "subscriptions_count",
    )
    list_editable = (
        "first_name",
        "last_name",
        "surname",
    )
    list_filter = (
        "username",
        "email",
        "phone_number",
        "last_name",
    )
    search_fields = (
        "username",
        "email",
        "phone_number",
    )
    list_display_links = (
        "username",
        "email",
        "phone_number",
    )
    ordering = ('username',)
    list_per_page = LIMIT_POSTS_PER_PAGE

    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Персональные данные', {'fields': (
            'first_name',
            'last_name',
            'email',
            'phone_number',
            'surname'
        )}),
        ('Права доступа', {'fields': (
            'is_active',
            'is_staff',
            'is_superuser',
            'groups',
            'user_permissions'
        )}),
        ('Даты', {'fields': (
            'last_login',
            'date_joined'
        )}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'username',
                'password1',
                'password2',
                'first_name',
                'last_name',
                'email',
                'phone_number',
                'surname',
                'is_active',
                'is_staff',
                'is_superuser',
                'groups',
                'user_permissions'
            )
        }),
    )

    def subscriptions_count(self, obj):
        return obj.subscriptions.count()
    subscriptions_count.short_description = 'Количество подписок'
