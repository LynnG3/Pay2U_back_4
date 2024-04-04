"""Сериализатор для приложений services, payments и users. """
import datetime
import random
import string
from datetime import timedelta
from urllib import request

from django.contrib.auth import get_user_model
from django.db.models import Max
from djoser.serializers import UserCreateSerializer, UserSerializer
from drf_extra_fields.fields import Base64ImageField
from payments.models import Cashback, Payment, TariffKind
from rest_framework import response, serializers, status
from rest_framework.authtoken.models import Token
from rest_framework.serializers import SerializerMethodField  # ValidationError
from services.models import Category, Rating, Service, Subscription

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
        max_cashback = obj.services.aggregate(
            max_cashback=Max('cashback_percentage')
        )["max_cashback"]
        return max_cashback

class ShortHistorySerializer(serializers.ModelSerializer):
    """Сериализатор истории покупок, для главного меню."""

    accumulated = serializers.SerializerMethodField()
    total_spent = serializers.SerializerMethodField()

    def get_accumulated(self, obj):
        """Получение накопленного кэшбека для главной страницы."""

        user = self.context.get("request").user
        cashbacks = Cashback.objects.filter(payment__user=user)
        accumulated = sum([cashback.amount for cashback in cashbacks])
        return accumulated

    def get_total_spent(self, obj):
        # по месяцам разбить и историю и верхнюю плашку потрачено за март
        """Получение суммы потраченных средств для главной страницы."""

        user = self.context.get("request").user
        payments = Payment.objects.filter(user=user)
        total_spent = sum(
            [payment.tariff_kind.cost_total for payment in payments]
        )
        return total_spent

    class Meta:
        model = Payment
        fields = (
            "accumulated",
            "total_spent",
        )


class ServiceImageSerializer(serializers.ModelSerializer):
    """Сериализатор для отображения только поля image в модели Subscription."""

    image = Base64ImageField()

    class Meta:
        model = Service
        fields = ("image",)


class SubscribedServiceSerializer(serializers.ModelSerializer):
    """Сериализатор чтения краткой информации о сервисах,
    на которые подписан пользователь,
    отображаемой в баннере на главной странице.
    """

    nearest_payment_date = serializers.SerializerMethodField()
    next_payment_amount = serializers.SerializerMethodField()

    def get_nearest_payment_date(self, obj):
        user = self.context.get("request").user
        nearest_payment = (
            Payment.objects.filter(user=user, service__pk=obj.pk)
            .order_by("next_payment_date")
            .first()
        )
        if nearest_payment:
            return nearest_payment.next_payment_date
        return None

    def get_next_payment_amount(self, obj):
        user = self.context.get("request").user
        next_payment_amount = (
            Payment.objects.filter(user=user, service=obj.service)
            .order_by("next_payment_date")
            .first()
        )
        if next_payment_amount:
            return next_payment_amount.tariff_kind.cost_total
        return None

    def to_representation(self, instance):
        data = super().to_representation(instance)
        return data

    class Meta:
        model = Service
        fields = (
            "nearest_payment_date",
            "next_payment_amount",
        )


class ServiceMainPageSerializer(serializers.ModelSerializer):
    """Получение инфо о сервисе."""

    is_subscribed = SubscribedServiceSerializer(
        many=True,
        source="subscriptions",
    )
    categories = CategorySerializer(source='category')
    new = SerializerMethodField()
    popular = SerializerMethodField()
    short_history = ShortHistorySerializer(source="payment_services")

    class Meta:
        model = Service
        fields = (
            "is_subscribed",
            "image",
            "short_history",
            "categories",
            "new",
            "popular",
        )
        read_only_fields = (
            "is_subscribed",
            "short_history",
            "categories",
            "new",
            "popular",
        )

    def get_new(self, obj):
        """Функция-счетчик для определения, является ли сервис новым."""
        today = datetime.date.today()
        delta_days = (today - obj.pub_date.date()).days
        return delta_days <= 60

    def get_popular(self, obj):
        """Получение состояния популярности."""

        user = self.context.get("request").user
        subscriptions = obj.subscriptions.filter(user=user)
        if subscriptions.count() >= 50:
            subscriptions.update(popular=True)
            return obj.popular
        return False


class SubscriptionSerializer(serializers.ModelSerializer):
    """Cериализатор подписки ."""

    # activation_status же уже есть в модели - нужно ли дублировать?
    # ACTIVATION_CHOICES = (
    #     (1, "Активирована"),
    #     (2, "недействительна"),
    #     (3, "ожидает активации"),
    # )
    # activation_status = serializers.ChoiceField(choices=ACTIVATION_CHOICES)

    service = serializers.PrimaryKeyRelatedField(
        queryset=Service.objects.all()
    )
    user = serializers.CurrentUserDefault()
    start_date = serializers.DateTimeField(read_only=True)
    expiry_date = serializers.DateTimeField(read_only=True)
    tariff = serializers.PrimaryKeyRelatedField(
        queryset=Payment.objects.select_related("tariff_kind").all()
    )

    class Meta:
        model = Subscription
        fields = "__all__"

    def create(self, validated_data):
        user = self.context['request'].user
        service = validated_data['service']
        trial = validated_data.get('trial', False)
        subscription, created = Subscription.objects.get_or_create(
            user=user, service=service, defaults=validated_data
        )
        # Проверка, существует ли подписка на пробный период
        # и пользователь подписывается на этот сервис впервые
        if trial and created:
            # Установка флага пробного периода
            validated_data['trial'] = True
            # Установка срока окончания пробного периода
            validated_data['expiry_date'] = (
                datetime.date.today() + datetime.timedelta(days=30)
            )
            Subscription.objects.create(**validated_data)
            return response.Response(
                {"message": "Пробный период подключен"},
                status=status.HTTP_201_CREATED
            )
        else:
            return subscription


class PaymentSerializer(serializers.ModelSerializer):
    """Cериализатор оплаты подписки ."""

    is_trial = SerializerMethodField()

    class Meta:
        model = Payment
        fields = "__all__"

    def get_is_trial(self, obj):
        # Получает связанную подписку из объекта платежа
        subscription = obj.subscription
        # Проверяем, является ли подписка пробным периодом
        return subscription.trial

    def create(self, validated_data):
        tariffs_payment = validated_data.get("tariff_kind")
        is_trial = self.get_is_trial(validated_data)
        if is_trial:
            tariffs_payment.cost_total = 1
        next_payment_date = validated_data.get("pub_date") + 30
        next_payment_amount = tariffs_payment.cost_total
        if validated_data.get("callback") is True:
            payment = Payment.objects.create(
                next_payment_amount, next_payment_date, **validated_data
            )
            return payment
        return super().create(validated_data)


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


class SellHistorySerializer(serializers.ModelSerializer):
    """Cериализатор истории платежей ."""

    service_name = serializers.CharField(source="service.name")
    service_image = Base64ImageField(source="service.image")
    payment_date = serializers.DateField(format="%d.%m.%y")
    amount = serializers.DecimalField(
        max_digits=8,
        decimal_places=2,
        source="cashbacks.amount"
    )

    class Meta:
        model = Payment
        fields = (
            "service_name",
            "service_image",
            "payment_date",
            "total",
            "amount"
        )


class RatingSerializer(serializers.ModelSerializer):
    average_ratings = SerializerMethodField()

    class Meta:
        model = Rating
        fields = "__all__"

    def get_average_retings(self, obj):
        ratings = Rating.objects.filter(service=obj)
        total_ratings = sum([rating.stars for rating in ratings])
        if ratings:
            return total_ratingsratings / len(ratings)
        return 0
