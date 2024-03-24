# from django.http import FileResponse
# from django.shortcuts import get_object_or_404
# from django_filters.rest_framework import DjangoFilterBackend
# from api.filters import ServicesFilter
# from api.permissions import IsOwnerOrReadOnly

from api.v1.serializers import (  # CustomUserGetSerializer, CustomUserSerializer
    CategorySerializer,
    CustomUserSerializer,
    RatingSerializer,
    ServiceSerializer,
    SubscriptionSerializer,
)
from django.contrib.auth import get_user_model
from djoser.views import UserViewSet
from rest_framework import authentication, status, views, viewsets
from rest_framework.authtoken.models import Token
from rest_framework.decorators import action

# from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import (
    AllowAny,
    IsAuthenticated,
    IsAuthenticatedOrReadOnly,
)
from rest_framework.response import Response
from services.models import Category, Service, Subscription

# from django.contrib.auth.models import User
# from payments.models import AutoPayment, Tarif, SellHistory


# class CommonPagination(PageNumberPagination): НЕ НУЖНА СКОРЕЕ ВСЕГО
#     """Пагинация."""
#     page_size = 6
#     page_size_query_param = 'limit'
User = get_user_model()


class CustomUserViewSet(UserViewSet):
    queryset = User.objects.all()
    serializer_class = CustomUserSerializer
    pagination_class = None

    def get_permissions(self):
        if self.action == 'me':
            return (IsAuthenticated(),)
        return super().get_permissions()


class ServiceViewSet(viewsets.ReadOnlyModelViewSet):
    """Представление списка сервисов/отдельного сервиса,
    Обрабатывает запросы к /api/services/ и /api/services/{id}/"""

    queryset = Service.objects.all()
    # permission_classes = [IsOwnerOrReadOnly, IsAuthenticatedOrReadOnly]
    # pagination_class = CommonPagination
    # filterset_class = ServicesFilter
    serializer_class = ServiceSerializer


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """Представление категорий - кино, музыка, книги итд."""

    serializer_class = CategorySerializer
    queryset = Category.objects.all()
    # pagination_class = None


class SubscriptionViewSet(viewsets.ViewSet):
    """Просмотр своих подписок и управления подписками на сервисы."""

    queryset = Subscription.objects.all()
    serializer_class = SubscriptionSerializer

    @action(detail=True, methods=['post'])
    def subscribe(self, request, pk=None):
        service = Service.objects.get(pk=pk)
        user = request.user
        subscription_query = Subscription.objects.get_or_create(
            user=user, service=service
        )
        if subscription_query[1]:
            return Response(
                {'message': 'Successfully subscribed'},
                status=status.HTTP_201_CREATED,
            )
        else:
            return Response(
                {'message': 'Already subscribed'}, status=status.HTTP_200_OK
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
                status=status.HTTP_204_NO_CONTENT,
            )
        except Subscription.DoesNotExist:
            return Response(
                {'message': 'Subscription not found'},
                status=status.HTTP_404_NOT_FOUND,
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