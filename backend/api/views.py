# from django.db.models import Sum
# from django.http import FileResponse
# from django.shortcuts import get_object_or_404
# from django_filters.rest_framework import DjangoFilterBackend
# from djoser.views import UserViewSet
from rest_framework import status
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
# from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
# from api.filters import ServicesFilter
from api.permissions import IsOwnerOrReadOnly
from api.serializers import (ServiceSerializer,
                             SubscriptionSerializer,
                             CategorySerializer,
                             RatingSerializer
                            #  CustomUserGetSerializer, CustomUserSerializer
                             )
from services.models import Service, Category, Rating, Subscription
from users.models import Subscription
# from django.contrib.auth.models import User
# from payments.models import AutoPayment, Tarif, SellHistory


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


class ServiceViewSet(viewsets.ReadOnlyModelViewSet):
    """Представление списка сервисов/отдельного сервиса,
    Обрабатывает запросы к /api/services/ и /api/services/{id}/"""

    queryset = Service.objects.all()
    # permission_classes = [IsOwnerOrReadOnly, IsAuthenticatedOrReadOnly]
    # pagination_class = CommonPagination
    # filterset_class = ServicesFilter
    serializer_class = ServiceSerializer


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """ Представление категорий - кино, музыка, книги итд. """

    serializer_class = CategorySerializer
    queryset = Category.objects.all()
    # pagination_class = None


class SubscriptionViewSet(viewsets.ViewSet):
    """ Просмотр своих подписок и управления подписками на сервисы. """

    queryset = Subscription.objects.all()
    serializer_class = SubscriptionSerializer

    @action(detail=True, methods=['post'])
    def subscribe(self, request, pk=None):
        service = Service.objects.get(pk=pk)
        user = request.user
        subscription_query = Subscription.objects.get_or_create(
            user=user,
            service=service
        )
        if subscription_query[1]:
            return Response(
                {'message': 'Successfully subscribed'},
                status=status.HTTP_201_CREATED
            )
        else:
            return Response(
                {'message': 'Already subscribed'},
                status=status.HTTP_200_OK
            )
        # subscription, created = subscription_query

        # if created:
        #     return Response(
        # {'message': 'Successfully subscribed'}, status=status.HTTP_201_CREATED)
        # else:
        #     return Response({'message': 'Already subscribed'}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['delete'])
    def unsubscribe(self, request, pk=None):
        service = Service.objects.get(pk=pk)
        user = request.user
        try:
            subscription = Subscription.objects.get(user=user, service=service)
            subscription.delete()
            return Response(
                {'message': 'Successfully unsubscribed'},
                status=status.HTTP_204_NO_CONTENT
            )
        except Subscription.DoesNotExist:
            return Response(
                {'message': 'Subscription not found'},
                status=status.HTTP_404_NOT_FOUND
            )


class RatingViewSet(viewsets.ModelViewSet):
    serializer_class = RatingSerializer
    queryset = Rating.objects.all()

    def get_permissions(self):
        if self.action == 'create':
            return [IsAuthenticated()]
        return [IsOwnerOrReadOnly()]

    @action(detail=False, methods=['put'])
    def update_rating(self, request):
        data = request.data
        try:
            rating = Rating.objects.get(
                user=request.user,
                service=data['service']
            )
            rating.stars = data['stars']
            rating.save()
            return Response(
                {'message': 'Rating updated successfully'},
                status=status.HTTP_200_OK
            )
        except Rating.DoesNotExist:
            return Response(
                {'error': 'Rating does not exist'},
                status=status.HTTP_404_NOT_FOUND
            )
