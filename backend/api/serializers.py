'''Сериализатор для приложений services, payments и users. '''
# import re
# from django.contrib.auth.models import User
# from djoser.serializers import UserCreateSerializer, UserSerializer
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
# from rest_framework.authtoken.models import Token
# from rest_framework.serializers import SerializerMethodField, ValidationError
# from rest_framework.validators import UniqueTogetherValidator
# from django.db.models import UniqueConstraint

from services.models import Category, Rating, Service, Subscription
# from users.models import CustomUser


# class CustomUserSerializer(UserCreateSerializer):
#     """Сериализатор создания/редактирования/удаления пользователя. """

#     email = serializers.EmailField()
#     username = serializers.CharField(required=True, max_length=150)
#     first_name = serializers.CharField(required=True, max_length=150)
#     last_name = serializers.CharField(required=True, max_length=150)

#     class Meta:
#         model = CustomUser
#         fields = (
#             'id',
#             'username',
#             'email',
#             'first_name',
#             'last_name',
#             'password',
#         )

#     def validate_username(self, username):

#         pattern = r'^[\w.@+-]+\Z'
#         if not re.match(pattern, username):
#             raise serializers.ValidationError(
#                 'Имя пользователя содержит недопустимый символ.'
#             )
#         return username


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
    """Сериализатор категории. """

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
    для новинок и популярного. """

    image = Base64ImageField()

    class Meta:
        model = Service
        fields = ('id', 'name', 'image')
        read_only_fields = ('id', 'name', 'image')


# class SubscriptionReadSerializer(serializers.ModelSerializer):
#     """Сериализатор просмотра подписок текущего пользователя. """

#     is_subscribed = SerializerMethodField()
#     services = serializers.SerializerMethodField()
    

#     class Meta:


# class SubscriptionSerializer(serializers.ModelSerializer):
#     """Сериализатор подписок. """

#     service = serializers.PrimaryKeyRelatedField(
#         queryset=Service.objects.all()
#     )
#     user = serializers.PrimaryKeyRelatedField(
#         queryset=User.objects.all()
#     )

#     class Meta:
#         model = Subscription
#         fields = ('user', 'service')
#         validators = (
#             UniqueTogetherValidator(
#                 queryset=Subscription.objects.all(),
#                 fields=('user', 'service'),
#                 message='Вы подписаны на этот сервис. '
#             ),
#         )

#     def to_representation(self, instance):
#         """Определяет сериализатор для чтения."""
#         service_instance = instance.service
#         return SubscriptionSerializer(
#             service_instance,
#             context={'request':
#                      self.context['request']}
#         ).data


class SubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscription
        fields = '__all__'


class RatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rating
        fields = '__all__'