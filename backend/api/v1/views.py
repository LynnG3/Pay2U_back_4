import datetime

from django.contrib.auth import get_user_model
from djoser.views import UserViewSet
from django.shortcuts import redirect
from payments.models import Payment, TariffKind
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from services.models import (
    Category,
    Rating,
    Service,
    Subscription,
)

from .permissions import IsOwner
from .serializers import (
    CategorySerializer,
    # CreateCustomUserSerializer,
    CustomUserSerializer,
    PaymentSerializer,
    PromocodeSerializer,
    RatingSerializer,
    ServiceMainPageSerializer,
    SubscribedServiceSerializer,
    SubscriptionSerializer,
    SellHistorySerializer
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

    def get_queryset(self):
        return Service.objects.filter(pub_date__lte=datetime.datetime.now())

    def list(self, request):
        services = self.get_queryset()
        serializer = SubscribedServiceSerializer(
            services, many=True, context={"request": request}
        )
        return Response(serializer.data, status=status.HTTP_200_OK)


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """Представление категорий - кино, музыка, книги итд."""

    serializer_class = CategorySerializer
    queryset = Category.objects.all()

    def list(self, request):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class SubscribeView(GenericAPIView):
    """Оформление подписки на сервис."""

    serializer_class = SubscriptionSerializer
    queryset = Subscription.objects.all()

    def post(self, request):
        service_id = request.data.get("service_id")
        user = request.user
        try:
            service = Service.objects.get(id=service_id)
        #     # Проверка на наличие активной подписки ДЛЯ ПРОБНОГО ПЕРИОДА
        #     existing_subscription = Subscription.objects.filter(user=user, service=service)
        #     if existing_subscription.exists():
        #         return Response(
        #             {"message": "Вы уже подписаны"},
        #             status=status.HTTP_400_BAD_REQUEST
        #         )
        #     subscription = Subscription.objects.create(user=user, service=service, trial=True)
        #     if subscription:
        #         return Response(status=status.HTTP_200_OK)
        # except Service.DoesNotExist:
        #     return Response(status=status.HTTP_404_NOT_FOUND)
            Subscription.objects.create(user=user, service=service)
            return Response(status=status.HTTP_200_OK)
        except Service.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)


class SubscriptionPaymentView(GenericAPIView):
    """Оплата подписки на сервис."""

    serializer_class = PaymentSerializer
    queryset = Payment.objects.all()

    def post(self, request):
        # логика оплаты - имитация
        callback = True
        # предполагаем, что оплата прошла успешно
        if callback:
            return redirect("subscription_paid")
            # return Response(
            #     {"message": "Успешная оплата"},
            #     status=status.HTTP_200_OK,
            # )
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
    queryset = Payment.objects.all()

    def get_queryset(self):
        user = self.request.user  # Получаем текущего пользователя
        return Payment.objects.filter(user=user)


class SubscriptionViewSet(viewsets.ViewSet):
    """Просмотр своих подписок и управления подписками на сервисы."""

    queryset = Subscription.objects.all()
    serializer_class = SubscriptionSerializer
    permission_classes = [IsOwner]

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

    @action(detail=True, methods=["patch"])
    def manage_subscription(self, request, pk=None):
        """Управление подпиской: сменить тариф или подключить автоплатеж."""
        action_type = request.data.get("action_type")
        try:
            subscription = Service.objects.get(pk=pk)
            if action_type == "change_tarif":
                new_tariff_id = request.data.get('tariff_id')
                new_tariff = TariffKind.objects.get(pk=new_tariff_id)
                subscription.tariff = new_tariff
                subscription.save()
                return Response(
                    {"message": "Тариф успешно изменен"},
                    status=status.HTTP_200_OK
                )
            elif action_type == "autopayment":
                # логика автооплаты или симуляция - нажал кнопку подключилась
                return Response(
                    {"message": "Автооплата успешно подключена"},
                    status=status.HTTP_200_OK
                )
            else:
                return Response(
                    {"message": "Неверный тип действия"},
                    status=status.HTTP_400_BAD_REQUEST
                )
        except Subscription.DoesNotExist:
            return Response(
                {"message": "Подписка не найдена"},
                status=status.HTTP_404_NOT_FOUND
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
