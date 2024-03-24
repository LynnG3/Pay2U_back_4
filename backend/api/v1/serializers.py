'''Сериализатор для приложений services, payments и users. '''

from tokenize import Token

from django.contrib.auth import get_user_model
from djoser.serializers import UserCreateSerializer, UserSerializer
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from services.models import Category, Rating, Service, Subscription

from rest_framework.authtoken.models import Token

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


# class SubscriptionMixin:

#     def get_is_subscribed(self, obj):
#         request = self.context.get('request')
#         if request is None or request.user.is_anonymous:
#             return False
#         return Subscription.objects.filter(user=request.user, author=obj.id).exists()


# class CustomUserGetSerializer(UserSerializer, SubscriptionMixin):
#     """Сериализатор для просмотра инфо пользователя. """

#     is_subscribed = SerializerMethodField()

#     class Meta:
#         model = CustomUser
#         fields = (
#             'id',
#             'username',
#             'email',
#             'first_name',
#             'last_name',
#             'is_subscribed'
#         )


# class PasswordSerializer(serializers.Serializer):
#     """Сериализатор смены пароля. """

#     new_password = serializers.CharField(required=True)
#     current_password = serializers.CharField(required=True)

#     class Meta:
#         model = CustomUser
#         fields = '__all__'


# class TokenSerializer(serializers.ModelSerializer):
#     """Сериализатор получения токена. """

#     token = serializers.CharField(source='key')

#     class Meta:
#         model = Token
#         fields = ('token',)


class CategorySerializer(serializers.ModelSerializer):
    """Сериализатор категории."""

    class Meta:
        model = Category
        fields = ('id', 'title', 'slug')


class ServiceSerializer(serializers.ModelSerializer):
    """Получение инфо о сервисе."""

    is_subscribed = serializers.SerializerMethodField()

    def get_is_subscribed(self, obj):
        """Получение своих подписок."""
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        user = request.user
        return Subscription.objects.filter(service=obj, user=user).exists()

    class Meta:
        model = Service
        fields = '__all__'


class NewPopularSerializer(serializers.ModelSerializer):
    """Cериализатор чтения сервисов
    для новинок и популярного."""

    image = Base64ImageField()

    class Meta:
        model = Service
        fields = ('id', 'name', 'image')
        read_only_fields = ('id', 'name', 'image')


class SubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscription
        fields = '__all__'


class RatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rating
        fields = '__all__'