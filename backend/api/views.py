from django.db.models import Sum
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from rest_framework import status
from rest_framework.decorators import action
# from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import (AllowAny,
                                        IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from api.filters import ServicesFilter
from api.permissions import IsOwnerOrReadOnly
from api.serializers import (
                            #  CustomUserGetSerializer, CustomUserSerializer,
                             ServiceSerializer,
                             CatalogSerializer,
                             SubscriptionReadSerializer,
                             SubscriptionManagementSerializer, SubscriptionConnectSerializer,
                             CategorySerializer)
from services.models import Service, Category
from users.models import CustomUser, Subscription
from payments.models import AutoPayment, Payment, SellHistory

# КАК РАЗДЕЛИТЬ СЕРВИСЫ ПО КАТАЛОГАМ : общий все показывать, 
# если поле новинка = тру то показывать
# если поле популяр = тру то показывать 
# каталог это кверисет сервисов, вопрос нужен ли отдельный эндпойнт для каталога?
# главная страница это
# сториз - как их оформлять? кверисет готовых страниц? нужен темплейтвью стори (????)


# class CommonPagination(PageNumberPagination): НЕ НУЖНА СКОРЕЕ ВСЕГО
#     """Пагинация."""
#     page_size = 6
#     page_size_query_param = 'limit'


# class CustomUserViewSet(UserViewSet):
#     """Api для работы с пользователями.
#     """

#     pagination_class = CommonPagination
#     permission_classes = [AllowAny, ]

#     def get_serializer_class(self):
#         if self.action in ['create', 'update', 'partial_update', 'delete']:
#             return CustomUserSerializer
#         elif self.request.method == 'GET':
#             return CustomUserGetSerializer
#         return super().get_serializer_class()

#     def get_permissions(self):
#         if self.action == 'me':
#             self.permission_classes = [IsAuthenticated]
#         return super().get_permissions()

#     @action(
#         methods=['delete', 'post'],
#         detail=True,
#         permission_classes=[IsAuthenticated],
#     )
#     def subscribe(self, request, id=None):
#         """Создание и удаление подписок.
#         Обработка запросов к '/api/users/{id}/subscribe/'
#         """
#         user = request.user
#         author = get_object_or_404(CustomUser, id=id)
#         follow = Follow.objects.filter(user=user, author=author)
#         data = {
#             'user': user.id,
#             'author': author.id,
#         }
#         if request.method == 'POST':
#             serializer = FollowSerializer(
#                 data=data,
#                 context={'request': request}
#             )
#             serializer.is_valid(raise_exception=True)
#             serializer.save()
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#         if follow.exists():
#             follow.delete()
#             return Response(
#                 f'Подписка на {author.username} отменена',
#                 status=status.HTTP_204_NO_CONTENT
#             )
#         return Response(
#             'Такой подписки не существует',
#             status=status.HTTP_400_BAD_REQUEST
#         )

#     @action(
#         methods=['get', 'post'],
#         detail=False,
#         permission_classes=[IsAuthenticated],
#     )
#     def subscriptions(self, request):
#         """Просмотр подписок пользователя.
#         Обработка запросов к '/api/users/subscriptions/
#         """
#         user = request.user
#         queryset = (
#             CustomUser.objects
#             .filter(author__user=user)
#         )
#         pages = self.paginate_queryset(queryset)
#         serializer = FollowReadSerializer(
#             pages,
#             many=True,
#             context={'request': request}
#         )
#         return self.get_paginated_response(serializer.data)


class ServiceViewSet(ReadOnlyModelViewSet):
    """Представление списка сервисов/отдельного сервиса,
    Обрабатывает запросы к /api/services/ и /api/services/{id}/"""

    queryset = Service.objects.all()
    permission_classes = [IsOwnerOrReadOnly, IsAuthenticatedOrReadOnly]
    # pagination_class = CommonPagination
    filterset_class = ServicesFilter
    serializer_class = ServiceSerializer


class CategoryViewSet(ReadOnlyModelViewSet):
    """ Представление категорий - кино, музыка, книги итд. """

    serializer_class = CategorySerializer
    queryset = Category.objects.all()
    pagination_class = None
