from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from users.models import CustomUser
from services.models import Subscription


class SubscriptionInline(admin.TabularInline):
    'Таблица с подписками пользователей. '

    model = Subscription
    fields = ['service', 'payment_status', 'activation_status', 'expiry_date']


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):

    inlines = [SubscriptionInline]
    list_display = (
        'username',
        'first_name',
        'last_name',
        'email',
        'phone_number',
        'surname',
        'subscriptions_count'
    )
    list_filter = ('username', 'email', 'phone_number',)
    search_fields = ('username', 'email', 'phone_number',)
    ordering = ('username',)

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

    def subscriptions_count(self, obj):
        return obj.subscriptions.count()
    subscriptions_count.short_description = 'Количество подписок'
