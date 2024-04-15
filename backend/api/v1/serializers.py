"""Сериализатор для приложений services, payments и users. """
import datetime
import random
import string
from datetime import datetime, timedelta

from django.contrib.auth import get_user_model
from django.db.models import Max
from django.shortcuts import get_object_or_404
from djoser.serializers import UserCreateSerializer, UserSerializer
from drf_extra_fields.fields import Base64ImageField
from rest_framework import response, serializers, status
from rest_framework.authtoken.models import Token
from rest_framework.serializers import SerializerMethodField

from payments.models import Cashback, TariffKind, Payment
from services.models import Category, Rating, Service, Subscription

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
    """Сериализатор категории для главной страницы."""

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


class ServiceShortSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = (
            "id",
            "name",
            "cashback_percentage",
            "image",
        )


class ServiceMainPageSerializer(serializers.ModelSerializer):
    """Получение инфо о сервисе."""

    image = SerializerMethodField()
    nearest_payment_date = SerializerMethodField()
    next_payment_amount = SerializerMethodField()
    short_history = ShortHistorySerializer(source="payment_services")
    new = SerializerMethodField()
    popular = SerializerMethodField()
    categories = SerializerMethodField()

    class Meta:
        model = Service
        fields = (
            "image",
            "nearest_payment_date",
            "next_payment_amount",
            "short_history",
            "new",
            "popular",
            "categories",
        )

    def get_average_ratings(self, obj):
        ratings = Rating.objects.filter(service=obj)
        total_ratings = sum([rating.stars for rating in ratings])
        if ratings:
            return total_ratings / len(ratings)
        return 0

    def get_image(self, obj):
        user = self.context.get("request").user
        subscriptions = user.subscriptions.all()
        images = [
            subscription.service.image.url for subscription in subscriptions
        ]
        return images

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
            Payment.objects.filter(user=user, service=obj)
            .order_by("next_payment_date")
            .first()
        )
        if next_payment_amount:
            return next_payment_amount.tariff_kind.cost_total
        return None

    def get_new(self, obj):
        """Функция-счетчик для определения, является ли сервис новым."""
        today = datetime.date.today()
        delta_days = (today - obj.pub_date.date()).days
        new_services = Service.objects.filter(new=True)
        if delta_days >= 60:
            obj.new = False
            obj.save()
            old_services = Service.objects.filter(new=False)
            return ServiceShortSerializer(old_services, many=True).data
        return ServiceShortSerializer(new_services, many=True).data

    def get_popular(self, obj):
        """Получение состояния популярности."""

        user = self.context.get("request").user
        subscriptions = obj.subscriptions.filter(user=user)
        if subscriptions.count() >= 50:
            obj.popular = True
            obj.save()
            popular_services = Service.objects.filter(popular=True)
            return ServiceShortSerializer(popular_services, many=True).data
        else:
            average_ratings = self.get_average_ratings(obj)
            if average_ratings <= 4:
                non_popular_services = Service.objects.filter(
                    rating__stars__lte=4
                )
                return ServiceShortSerializer(
                    non_popular_services, many=True
                ).data
            popular_services = Service.objects.filter(rating__stars__gt=4)
            return ServiceShortSerializer(popular_services, many=True).data

    def get_categories(self, obj):

        categories = Category.objects.all()
        categories_data = CategorySerializer(categories, many=True).data

        return categories_data


class RatingSerializer(serializers.ModelSerializer):
    average_ratings = SerializerMethodField()

    class Meta:
        model = Rating
        fields = "__all__"

    def get_average_ratings(self, obj):
        ratings = Rating.objects.filter(service=obj)
        total_ratings = sum([rating.stars for rating in ratings])
        if ratings:
            return total_ratings / len(ratings)
        return 0


class CategoriesSerializer(serializers.ModelSerializer):
    """Сериализатор для подробного отображения содержания категории."""

    average_ratings = SerializerMethodField()

    class Meta:
        model = Service
        fields = (
            "id",
            "name",
            "cashback_percentage",
            "text",
            "image",
            "cost",
            "average_ratings",
        )

    def get_average_ratings(self, obj):
        ratings = Rating.objects.filter(service=obj)
        total_ratings = sum([rating.stars for rating in ratings])
        if ratings:
            return total_ratings / len(ratings)
        return 0


class ServiceSerializer(serializers.ModelSerializer):

    category = serializers.ReadOnlyField(source="category.title")

    class Meta:
        model = Service
        fields = (
            "id",
            "name",
            "image",
            "category",
            "text",
            "cost",
            "cashback_percentage",
            "new",
            "popular",
            "pub_date",
            "partners_link",
        )


class TariffKindSerializer(serializers.ModelSerializer):
    """Cериализатор информации о тарифе. """

    class Meta:
        model = TariffKind
        fields = (
            "id",
            "name",
            "duration",
            "cost_per_month",
            "cost_total",
            "description"
        )


class SubscribeSerializer(serializers.ModelSerializer):
    """Cериализатор оформления подписки на сервис."""

    tariffs = SerializerMethodField()

    class Meta:
        model = Service
        fields = (
            "id",
            "name",
            "image",
            "cashback_percentage",
            "tariffs"
        )

    def get_tariffs(self, obj):
        # Метод для получения данных о тарифах для сервиса
        tariffs = TariffKind.objects.filter(service=obj)
        serializer = TariffKindSerializer(tariffs, many=True)
        return serializer.data


class SubscriptionSerializer(serializers.ModelSerializer):
    """Cериализатор подписки."""

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
        model = Service
        fields = "__all__"

    def create(self, validated_data):
        user = self.context['request'].user
        service = validated_data['service']
        trial = validated_data.get('trial', False)
        subscription, created = Subscription.objects.get_or_create(
            user=user, service=service, defaults=validated_data
        )
        if trial and created:
            validated_data['trial'] = True
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

    service_id = serializers.IntegerField(write_only=True)
    # user = serializers.IntegerField(write_only=True)
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    # tariff_kind = serializers.PrimaryKeyRelatedField(
    #     queryset=TariffKind.objects.all()
    # )
    tariff_kind_id = serializers.IntegerField(write_only=True)
    total = serializers.ReadOnlyField()
    is_trial = SerializerMethodField()

    class Meta:
        model = Payment
        fields = (
            "id",
            "user",
            "service_id",
            "tariff_kind_id",
            "total",
            "accept_rules",
            "is_trial",
            "payment_date",
            "next_payment_date",
            "next_payment_amount"
        )

    def get_is_trial(self, instance):
        """Определяет доступность пробного периода."""
        if not instance:
            return False  # Возвращаем False если экземпляр не установлен
        past_payments = Payment.objects.filter(
            service=instance.service, user=instance.user
        )
        return not past_payments.exists()

    def get_next_payment_date(self, obj):
        """Возвращает дату следующего платежа."""
        if 'tariff_kind' in self.context:
            tariff_kind = self.context['tariff_kind']
            return datetime.now().date() + timedelta(days=30 * tariff_kind.duration)
        return None

    def get_next_payment_amount(self, obj):
        """Возвращает сумму следующего платежа."""
        if 'tariff_kind' in self.context:
            tariff_kind = self.context['tariff_kind']
            return tariff_kind.cost_total
        return None
    
    def create(self, validated_data):
        print(validated_data)
        service_id = validated_data.pop('service_id')
        tariff_kind_id = validated_data.pop('tariff_kind_id')
        user = validated_data.pop('user')
        service = get_object_or_404(Service, pk=service_id)
        tariff_kind = get_object_or_404(TariffKind, pk=tariff_kind_id)
        # Рассчитываем дату следующего платежа
        # current_payment_date = datetime.now().date()
        payment = Payment.objects.create(
            service=service,
            user=user,
            tariff_kind=tariff_kind,
            # next_payment_date=datetime.now().date() + timedelta(
            #     days=30 * tariff_kind.duration
            # ),
            # next_payment_amount=tariff_kind.cost_total,
            **validated_data
        )
        self.instance = payment
        is_trial = self.get_is_trial(payment)
        if is_trial:
            payment.total = 1
        else:
            payment.total = tariff_kind.cost_total
        payment.next_payment_date = self.get_next_payment_date(payment)
        payment.next_payment_amount = self.get_next_payment_amount(payment)
        payment.save()
        return payment

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['is_trial'] = self.get_is_trial(instance)
        return data


class PaymentGetSerializer(serializers.ModelSerializer):
    """Cериализатор просмотра данных оплаты подписки ."""


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
            "amount",
        )
