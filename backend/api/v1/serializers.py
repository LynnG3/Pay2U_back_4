"""Сериализатор для приложений services, payments и users. """
<<<<<<< Updated upstream
import random
import string
from datetime import timedelta
=======
>>>>>>> Stashed changes

from django.contrib.auth import get_user_model
from django.db.models import Max
from djoser.serializers import UserCreateSerializer, UserSerializer
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from rest_framework.authtoken.models import Token
from services.models import Category, Rating, Service, Subscription
from payments.models import Payment

# from rest_framework.serializers import SerializerMethodField, ValidationError
# from rest_framework.validators import UniqueTogetherValidator
# from django.db.models import UniqueConstraint
User = get_user_model()


class CustomUserSerializer(UserSerializer):
    """Сериализатор для кастомной модели пользователя."""


class Meta:
    model = User
    fields = (
        "id",
        "phone_number",
        "username",
        "first_name",
        "last_name",
        "surname",
        "email",
    )


class CreateCustomUserSerializer(UserCreateSerializer):
    """Сериализатор для создания кастомной модели пользователя."""

    class Meta:
        model = User
        fields = (
            "email",
            "phone_number",
            "id",
            "username",
            "first_name",
            "last_name",
            "surname",
            "password",
        )
        extra_kwargs = {
            "password": {"write_only": True},
            "email": {"required": True},
            "phone_number": {"required": True},
            "first_name": {"required": True},
            "last_name": {"required": True},
            "surname": {"required": True},
        }


class TokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = Token
        fields = ("key",)


class CategorySerializer(serializers.ModelSerializer):
    """Сериализатор категории."""

    image = Base64ImageField()
    max_cashback = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = (
            "id",
            "image",
            "title",
            "max_cashback",
        )
        read_only_fields = (
            "id",
            "image",
            "title",
            "max_cashback",
        )

    def get_max_cashback(self, obj):
        max_cashback = obj.category.annotate(
            max_cashback=Max('category__service_set__cashback')
        )
        return max_cashback


class NewPopularSerializer(serializers.ModelSerializer):
    """Cериализатор чтения сервисов
    для каталогов - новинки и популярное."""

    image = Base64ImageField()

    class Meta:
        model = Service
        fields = (
            "id",
            "name",
            "image",
            "cashback",
        )
        read_only_fields = (
            "id",
            "name",
            "image",
            "cashback",
        )


class SubscribedServiceSerializer(serializers.ModelSerializer):
    """Сериализатор чтения краткой информации о сервисах,
    на которые подписан пользователь,
    отображаемой в баннере на главной странице.
    """
<<<<<<< Updated upstream
    expiry_date = serializers.SerializerMethodField()
    activation_status = serializers.SerializerMethodField()

    def get_expiry_date(self, obj):
        """Получение даты следуюещй оплаты."""

        return Subscription.objects.get('expire_date')
=======
    expire_date = serializers.SerializerMethodField()
    activation_status = serializers.SerializerMethodField()

    def get_expire_date(self):
        """Получение даты следуюещй оплаты."""

        return Subscription.objects.get(expire_date)
>>>>>>> Stashed changes

    def get_activation_status(self, obj):
        """Получение статуса подписки."""

        user = self.context.get("request").user
        return Subscription.objects.filter(service=obj, user=user).exists()

    class Meta:
        model = Service
        fields = (
            "image",
<<<<<<< Updated upstream
            "expiry_date",
=======
            "expire_date",
>>>>>>> Stashed changes
            "activation_status",
        )  # "next_sum",


class ServiceSerializer(serializers.ModelSerializer):
    """Получение инфо о сервисе."""

    is_subscribed = SubscribedServiceSerializer(many=True)
    image = Base64ImageField()
    categories = CategorySerializer(many=True)
    new = NewPopularSerializer(many=True)
    popular = NewPopularSerializer(many=True)

    # def get_is_subscribed(self, obj):
    #     """Получение своих подписок."""
    #     user = self.context.get("request").user
    #     return Subscription.objects.filter(service=obj, user=user).exists()

    class Meta:
        model = Service
        fields = (
            "name",
            "image",
            "text",
            "cost",
            "cashback",
            "is_subscribed",
            "new",
            "popular",
            "categories",
        )


class SubscriptionSerializer(serializers.ModelSerializer):
    """Cериализатор подписки ."""

    ACTIVATION_CHOICES = (
        (1, "Активирована"),
        (2, "недействительна"),
        (3, "ожидает активации"),
    )

    activation_status = serializers.ChoiceField(choices=ACTIVATION_CHOICES)

    class Meta:
        model = Subscription
        fields = "__all__"

    # def get_activation_status(self, obj):
    #     """Получение статуса подписки."""
    #     request = self.context.get('request')
    #     if request is None or request.user.is_anonymous:
    #         return False
    #     user = request.user
    #     return Subscription.objects.filter(service=obj, user=user).exists()


class PaymentSerializer(serializers.ModelSerializer):
    """Cериализатор оплаты подписки ."""

    class Meta:
        model = Payment
        fields = "__all__"


class PromocodeSerializer(serializers.ModelSerializer):
    """Cериализатор страницы с промокодом ."""

    promo_code = serializers.SerializerMethodField()
    promo_code_expiry_date = serializers.SerializerMethodField()

    class Meta:
        model = Payment
        fields = (
            "total",
            "promo_code",
            "promo_code_expiry_date"
        )

    def get_promo_code(self, obj):
        promo_code = "".join(
            random.choices(string.ascii_letters + string.digits, k=12)
        )
        return promo_code

    def get_promo_code_expiry_date(self, obj):
        return obj.payment_date + timedelta(days=7)


class RatingSerializer(serializers.ModelSerializer):

    class Meta:
        model = Rating
        fields = "__all__"
