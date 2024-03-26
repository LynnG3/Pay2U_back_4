# from django.http import FileResponse
# from django.shortcuts import get_object_or_404
# from django_filters.rest_framework import DjangoFilterBackend
# from api.filters import ServicesFilter
import datetime
import random
import string

from django.contrib.auth import get_user_model
# from django.shortcuts import redirect
from djoser.views import UserViewSet
from rest_framework import status, viewsets
# from rest_framework.authtoken.models import Token
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from api.v1.permissions import IsOwner
from api.v1.serializers import (CategorySerializer,
                                CustomUserSerializer,
                                NewPopularSerializer,
                                RatingSerializer,
                                ServiceSerializer,
                                SubscribedServiceSerializer,
                                SubscriptionSerializer)
# from payments.models import AutoPayment, Tarif, SellHistory
from services.models import Category, Rating, Service, Subscription


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
    """Представление главной страницы,
    списков сервисов и отдельного сервиса,
    Обрабатывает запросы к главной странице,
    каталогам сервисов и странице отдельного сервиса.
    """

    queryset = Service.objects.all()
    # filterset_class = ServicesFilter
    serializer_class = ServiceSerializer

    def get_queryset(self):
        queryset = self.queryset

        # представления на главной странице
        if self.request.path == '/services/':
            if 'new' in self.request.query_params:
                queryset = Service.objects.filter(is_new=True)
            elif 'popular' in self.request.query_params:
                queryset = Service.objects.filter(is_popular=True)
            elif 'is_subscribed' in self.request.query_params:
                queryset = Service.objects.filter(is_subscribed=True)
        return queryset

    def list(self, request):
        """Список категорий на главной странице для перехода по
        каталогам категорий.
        """
        queryset = self.filter_queryset(self.get_queryset())
        category_queryset = Category.objects.all()
        context = {'request': request}
        serializer = self.get_serializer(queryset, context=context, many=True)
        category_serializer = CategorySerializer(category_queryset, many=True)
        data = {
            'services': serializer.data,
            'categories': category_serializer.data,
        }
        return Response(data)

    def get_serializer_class(self):
        if self.request.path == '/services/':
            if 'is_subscribed' in self.request.query_params:
                return SubscribedServiceSerializer
            elif (
                'new' in self.request.query_params
                or 'popular' in self.request.query_params
            ):
                return NewPopularSerializer
            return ServiceSerializer
        return super().get_serializer_class()


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """Представление категорий - кино, музыка, книги итд."""

    serializer_class = CategorySerializer
    queryset = Category.objects.all()

    def list(self, request):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def get_queryset(self):
        return self.queryset


class SubscribeView(APIView):
    """Оформление подписки на сервис."""
    # мб лучше к ServiceViewSet с декоратором и/или миксином?

    def post(self, request):
        service_id = request.data.get('service_id')
        user = request.user
        try:
            service = Service.objects.get(id=service_id)
            Subscription.objects.create(user=user, service=service)
            return Response(status=status.HTTP_200_OK)
        except Service.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)


class SubscriptionPaymentView(APIView):
    """Оплата подписки на сервис."""

    def post(self, request):
        # логика оплаты (ввод карты и получение ответа от банка)- ???
        callback = True
        # типа оплата прошла
        # или разобр как запросить ответ у стороннего сервера,закомментить это
        if callback:
            return Response(status=status.HTTP_200_OK)
        else:
            return Response(
                {'message': 'Проблема на стороне банка'},
                status=status.HTTP_404_NOT_FOUND,
            )
        # обработать ошибку иначе и переадресовать
        # на кастомный шаблон error/bank или error/nomoney


class SubscriptionPaidView(APIView):
    """Страница с промокодом после успешной оплаты подписки."""

    def post(self, request):
        subscription = Subscription.objects.get(
            user=request.user,
            payment_status=True
        )
        promo_code = ''.join(
            random.choices(string.ascii_letters + string.digits, k=12)
        )
        expiry_date = datetime.date.today() + datetime.timedelta(days=30)
        subscription.promo_code = promo_code
        subscription.expiry_date = expiry_date
        subscription.save()
        return Response(status=status.HTTP_200_OK)


class SubscriptionViewSet(viewsets.ViewSet):
    """Просмотр своих подписок и управления подписками на сервисы."""

    queryset = Subscription.objects.all()
    serializer_class = SubscriptionSerializer
    permission_classes = [IsOwner]

    @action(detail=True, methods=['delete'])
    def unsubscribe(self, request, pk=None):
        """Отменить подписку."""
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

    @action(detail=True, methods=['patch'])
    def change_tarif(self, request, pk=None):
        """Сменить тариф."""
        pass

    @action(detail=True, methods=['patch'])
    def autopayment(self, request, pk=None):
        """Подключить автооплату."""
        pass


class RatingViewSet(viewsets.ModelViewSet):
    serializer_class = RatingSerializer
    queryset = Rating.objects.all()

    def get_permissions(self):
        if self.action == 'create':
            return [IsOwner()]
        return [IsAuthenticated()]

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
