"""Сериализатор для приложений services, payments и users. """
import datetime
import random
import string
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.db.models import Max
from djoser.serializers import UserCreateSerializer, UserSerializer
from drf_extra_fields.fields import Base64ImageField
from rest_framework import response, serializers, status
from rest_framework.authtoken.models import Token
from services.models import Category, Rating, Service, Subscription
from payments.models import Payment, Cashback, TariffKind

from rest_framework.serializers import SerializerMethodField  # ValidationError
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
        max_cashback = obj.service_set.aggregate(
            max_cashback=Max('cashback_percantage')
        )["max_cashback"]
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
            "cashback_percentage",
        )
        read_only_fields = (
            "id",
            "name",
            "image",
            "cashback_percentage",
        )


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
            [payment.tarrif_kind.cost_total for payment in payments]
        )
        return total_spent

    class Meta:
        model = Payment
        fields = (
            "accumulated",
            "total_spent",
        )


class SubscribedServiceSerializer(serializers.ModelSerializer):
    """Сериализатор чтения краткой информации о сервисах,
    на которые подписан пользователь,
    отображаемой в баннере на главной странице.
    """

    # image = serializers.SerializerMethodField()
    activation_status = serializers.SerializerMethodField()
    nearest_payment_date = serializers.SerializerMethodField()
    next_payment_amount = serializers.SerializerMethodField()

    def get_activation_status(self, obj):
        """Получение статуса подписки."""

        user = self.context.get("request").user
        return Subscription.objects.filter(service=obj, user=user).exists()

    # def get_image(self, obj):
    #     """Получение картинок для банннера подписок юзера."""
    #
    #     user = self.context.get("request").user
    #     return (
    #         Subscription.objects.filter(user=user, service=obj)
    #         .values("image")
    #         .first()
    #         .get("image")
    #     )

    def get_nearest_payment_date(self, obj):
        user = self.context.get("request").user
        nearest_payment_date = (
            Payment.objects.filter(user=user, service=obj)
            .order_by("next_payment_date")
            .first()
        )
        if nearest_payment_date:
            return PaymentSerializer(nearest_payment_date).data
        return None

    def get_next_payment_amount(self, obj):
        user = self.context.get("request").user
        next_payment_amount = (
            Payment.objects.filter(user=user, service=obj)
            .order_by("next_payment_date")
            .first()
        )
        if next_payment_amount:
            return PaymentSerializer(next_payment_amount)
        return None

    def to_representation(self, instance):
        data = super().to_representation(instance)
        return data

    class Meta:
        model = Service
        fields = (
            "image",
            "activation_status",
            "nearest_payment_date",
            "next_payment_amount",
        )


class ServiceMainPageSerializer(serializers.ModelSerializer):
    """Получение инфо о сервисе."""

    is_subscribed = SubscribedServiceSerializer(
        many=True,
        source="subscriptions",
    )
    categories = CategorySerializer(many=True)
    new = NewPopularSerializer(many=True)
    popular = NewPopularSerializer(many=True)
    short_history = ShortHistorySerializer(source="payment_services")

    class Meta:
        model = Service
        fields = (
            "is_subscribed",
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
        queryset=TariffKind.objects.all()
    )

    class Meta:
        model = Subscription
        fields = "__all__"

    def create(self, validated_data):
        user = self.context['request'].user
        service = validated_data['service']
        trial = validated_data.get('trial', False)
        previous_payments = Payment.objects.filter(
            user=user, service=service
        )
        previous_suscriptions = Subscription.objects.filter(
            user=user, service=service
        )
        # Проверка, существует ли подписка на пробный период 
        # и пользователь подписывается на этот сервис впервые
        if trial and (
            previous_suscriptions.count()
            and previous_payments.count()
        ) == 0:
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
            return super().create(validated_data)


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

    class Meta:
        model = Rating
        fields = "__all__"
