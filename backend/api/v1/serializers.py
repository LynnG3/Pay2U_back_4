'''Сериализатор для приложений services, payments и users. '''

from tokenize import Token

from django.contrib.auth import get_user_model
from djoser.serializers import UserCreateSerializer, UserSerializer
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from rest_framework.authtoken.models import Token

from services.models import Category, Rating, Service, Subscription

# from rest_framework.serializers import SerializerMethodField, ValidationError
# from rest_framework.validators import UniqueTogetherValidator
# from django.db.models import UniqueConstraint
User = get_user_model()


class CustomUserSerializer(UserSerializer):
    """Сериализатор для кастомной модели пользователя."""


class Meta:
    model = User
    fields = (
        'id',
        'phone_number',
        'username',
        'first_name',
        'last_name',
        'surname',
        'email',
    )


class CreateCustomUserSerializer(UserCreateSerializer):
    """Сериализатор для создания кастомной модели пользователя."""

    class Meta:
        model = User
        fields = (
            'email',
            'phone_number',
            'id',
            'username',
            'first_name',
            'last_name',
            'surname',
            'password',
        )
        extra_kwargs = {
            'password': {'write_only': True},
            'email': {'required': True},
            'phone_number': {'required': True},
            'first_name': {'required': True},
            'last_name': {'required': True},
            'surname': {'required': True},
        }


class TokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = Token
        fields = ('key',)


class CategorySerializer(serializers.ModelSerializer):
    """Сериализатор категории."""

    image = Base64ImageField()

    class Meta:
        model = Category
        fields = ('id', 'image', 'title')


class ServiceSerializer(serializers.ModelSerializer):
    """Получение инфо о сервисе."""

    is_subscribed = serializers.SerializerMethodField()
    image = Base64ImageField()

    def get_subscriptions(self, obj):
        """Получение своих подписок."""
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        user = request.user
        return Subscription.objects.filter(service=obj, user=user).exists()

    class Meta:
        model = Service
        fields = (
            'name',
            'image',
            'text',
            'cost',
            'cashback',
            'is_subscribed'
        )


class SubscribedServiceSerializer(serializers.ModelSerializer):
    """Сериализатор чтения краткой информации о сервисах,
    на которые подписан пользователь,
    отображаемой в баннере на главной странице.
    """

    class Meta:
        model = Service
        fields = ('image',)


class NewPopularSerializer(serializers.ModelSerializer):
    """Cериализатор чтения сервисов
    для каталогов - новинки и популярное."""

    image = Base64ImageField()

    class Meta:
        model = Service
        fields = ('id', 'name', 'image', 'cashback')
        read_only_fields = ('id', 'name', 'image', 'cashback')


class SubscriptionSerializer(serializers.ModelSerializer):
    """Cериализатор подписки ."""

    activation_status = serializers.SerializerMethodField()

    class Meta:
        model = Subscription
        fields = '__all__'

    # def get_activation_status(self, obj):
    #     """Получение статуса подписки."""
    #     request = self.context.get('request')
    #     if request is None or request.user.is_anonymous:
    #         return False
    #     user = request.user
    #     return Subscription.objects.filter(service=obj, user=user).exists()


class RatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rating
        fields = '__all__'
