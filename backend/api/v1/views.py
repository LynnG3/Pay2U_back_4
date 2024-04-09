import datetime

from django.contrib.auth import get_user_model
from django.shortcuts import redirect
from djoser.views import UserViewSet
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import (
    IsAuthenticated,
    IsAuthenticatedOrReadOnly,
)
from rest_framework.response import Response
from rest_framework.views import APIView

from payments.models import Payment, TariffKind
from services.models import Category, Rating, Service, Subscription
from .permissions import IsOwner
from .serializers import (
    CategoriesSerializer,
    CategorySerializer,
    CustomUserSerializer,
    PaymentSerializer,
    PromocodeSerializer,
    RatingSerializer,
    SellHistorySerializer,
    ServiceMainPageSerializer,
    ServiceSerializer,
    SubscriptionSerializer,
)

User = get_user_model()


class CustomUserViewSet(UserViewSet):
    queryset = User.objects.all()
    serializer_class = CustomUserSerializer
    pagination_class = None

    def get_permissions(self):
        if self.action == "me":
            return (IsAuthenticated(),)
        return super().get_permissions()


class ServiceViewSet(viewsets.ReadOnlyModelViewSet):
    """Представление главной страницы,
    списков сервисов и отдельного сервиса,
    Обрабатывает запросы к главной странице,
    каталогам сервисов и странице отдельного сервиса.
    """

    serializer_class = ServiceMainPageSerializer
    queryset = Service.objects.all()
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get_serializer_class(self):
        if self.action == "retrieve":
            return ServiceSerializer
        return super().get_serializer_class()

    def get_queryset(self):
        return Service.objects.filter(pub_date__lte=datetime.datetime.now())


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """Представление категорий - кино, музыка, книги итд."""

    serializer_class = CategorySerializer
    queryset = Category.objects.all()


class CategoriesViewSet(viewsets.ReadOnlyModelViewSet):
    """Представление отдельных категорий со всеми сервисами."""

    serializer_class = CategoriesSerializer
    queryset = Service.objects.select_related("services").all()


class SubscribeView(GenericAPIView):
    """Оформление подписки на сервис."""

    serializer_class = SubscriptionSerializer
    queryset = Subscription.objects.all()

    def post(self, request):
        service_id = request.data.get("service_id")
        user = request.user
        try:
            service = Service.objects.get(id=service_id)
            Subscription.objects.create(user=user, service=service)
            return Response(status=status.HTTP_200_OK)
        except Service.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)


@action()

class SubscriptionPaymentView(GenericAPIView):
    """Оплата подписки на сервис."""

    serializer_class = PaymentSerializer
    queryset = Payment.objects.all()

    def post(self, request):
        callback = True
        if callback:
            return redirect("subscription_paid")
        else:
            return Response(
                {"message": "Проблема на стороне банка"},
                status=status.HTTP_404_NOT_FOUND,
            )


class SubscriptionPaidView(APIView):
    """Страница с промокодом - открывается
    после успешной оплаты подписки."""

    def post(self, request):
        total = request.data.get('total')
        serializer = PromocodeSerializer(data={'total': total})
        serializer.is_valid(raise_exception=True)
        promo_code = serializer.data.get('promo_code')
        promo_code_expiry_date = serializer.data.get('promo_code_expiry_date')

        return Response(
            {
                'total': total,
                'promo_code': promo_code,
                'promo_code_expiry_date': promo_code_expiry_date,
            },
            status=status.HTTP_200_OK,
        )


class SellHistoryViewSet(viewsets.ReadOnlyModelViewSet):

    serializer_class = SellHistorySerializer
    queryset = Payment.objects.select_related("payment_users").all()
    permission_classes = (IsOwner,)

    # def get_queryset(self):
    #     user = self.request.user
    #     return Payment.objects.filter(user=user)


class SubscriptionViewSet(viewsets.ViewSet):
    """Просмотр своих подписок и управления подписками на сервисы."""

    queryset = Subscription.objects.all()
    serializer_class = SubscriptionSerializer
    permission_classes = [IsOwner]

    def activate_autopayment(self, request, pk=None):
        try:
            subscription = Subscription.objects.get(pk=pk)
            if subscription.autopayment:
                return Response(
                    {"message": "Автоплатеж уже активирован"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            else:
                subscription.autopayment = True
                subscription.save()
                return Response(
                    {"message": "Автоплатеж успешно активирован"},
                    status=status.HTTP_200_OK,
                )
        except Subscription.DoesNotExist:
            return Response(
                {"message": "Подписка не найдена"},
                status=status.HTTP_404_NOT_FOUND,
            )

    @action(detail=True, methods=["delete"])
    def unsubscribe(self, request, pk=None):
        """Отменить подписку."""
        service = Service.objects.get(pk=pk)
        user = request.user
        try:
            subscription = Subscription.objects.get(user=user, service=service)
            subscription.delete()
            return Response(
                {"message": "Successfully unsubscribed"},
                status=status.HTTP_204_NO_CONTENT,
            )
        except Subscription.DoesNotExist:
            return Response(
                {"message": "Subscription not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

    @action(detail=True, methods=["patch, post"])
    def autopayment(self, request, pk=None):
        self.activate_autopayment(request, pk)

    @action(detail=True, methods=["patch"])
    def manage_subscription(self, request, pk=None):
        """Управление подпиской: сменить тариф или подключить автоплатеж."""
        action_type = request.data.get("action_type")
        try:
            subscription = Subscription.objects.get(pk=pk)
            if action_type == "change_tariff":
                new_tariff_id = request.data.get('tariff_id')
                new_tariff = TariffKind.objects.get(pk=new_tariff_id)
                subscription.tariff = new_tariff
                subscription.save()
                return Response(
                    {"message": "Тариф успешно изменен"},
                    status=status.HTTP_200_OK,
                )
            else:
                return Response(
                    {"message": "Неверный тип действия"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        except Subscription.DoesNotExist:
            return Response(
                {"message": "Подписка не найдена"},
                status=status.HTTP_404_NOT_FOUND,
            )

    @action(detail=True, methods=["patch"])
    def change_tariff(self, request, pk=None):
        return self.manage_subscription(
            request, action_type="change_tariff", pk=pk
        )


class RatingViewSet(viewsets.ModelViewSet):
    serializer_class = RatingSerializer
    queryset = Rating.objects.all()

    def get_permissions(self):
        if self.action == "create":
            return [IsOwner()]
        return [IsAuthenticated()]

    @action(detail=True, methods=["put"])
    def update_rating(self, request):
        data = request.data
        try:
            rating = Rating.objects.get(
                user=request.user, service=data["service"]
            )
            rating.stars = data["stars"]
            rating.save()
            return Response(
                {"message": "Rating updated successfully"},
                status=status.HTTP_200_OK,
            )
        except Rating.DoesNotExist:
            return Response(
                {"error": "Rating does not exist"},
                status=status.HTTP_404_NOT_FOUND,
            )
