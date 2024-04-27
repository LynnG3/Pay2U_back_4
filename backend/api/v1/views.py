import datetime

from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from rest_framework import status, viewsets
from rest_framework.decorators import action
# from rest_framework.generics import GenericAPIView
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
    PaymentPostSerializer,
    PromocodeSerializer,
    RatingSerializer,
    SellHistorySerializer,
    ServiceMainPageSerializer,
    ServiceSerializer,
    SubscribeSerializer,
    SubscriptionSerializer,
    # TariffKindSerializer
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
    """Представление сервисов на главной странице.
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


class SubscribeViewSet(viewsets.GenericViewSet):
    """Оформление подписки на сервис."""

    serializer_class = SubscribeSerializer
    # queryset = Service.objects.all()

    def get_object(self, service_id):
        object = Service.objects.filter(id=service_id).first()
        return object

    def retrieve(self, request, pk=None):
        service = self.get_object(pk)
        if service:
            serializer = self.serializer_class(service)
            return Response(serializer.data)
        return Response({"error": "Сервис не найден"}, status=404)


class SubscriptionPaymentViewSet(viewsets.ViewSet):
    """Оплата подписки на сервис."""

    serializer_class = PaymentSerializer

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update', 'delete']:
            return PaymentPostSerializer
        return PaymentSerializer

    def create(self, request, *args, **kwargs):
        serializer_class = self.get_serializer_class()
        serializer = serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Получение объектов сервиса и тарифа из данных запроса
        service_id = request.data.get('service_id')
        tariff_kind_id = request.data.get('tariff_kind_id')

        # Проверка наличия идентификаторов сервиса и тарифа
        if not service_id or not tariff_kind_id:
            return Response(
                {"message": "Не указаны идентификаторы сервиса или тарифа"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Передача идентификаторов сервиса и тарифа в контекст сериализатора
        serializer = serializer_class(
            data=request.data,
            context={'request': request, 'service_id': service_id, 'tariff_kind_id': tariff_kind_id}
        )
        serializer.is_valid(raise_exception=True)

        # Создание объекта платежа
        payment = serializer.save()

        # Отправка данных на стороннее API банка
        # bank_api_url = "https://api.bank.com/payments"
        # payment_data = {
        #     "name": payment.tariff_kind.name,
        #     "amount": payment.total,
        #     "user_data": {
        #         "username": request.user.username,
        #         "email": request.user.email,
        #     },
        #     "card_number":...
        # }

        callback = True  # Имитация успешной обработки платежа
        if callback:
            payment.save()
            data = serializer.data
            return Response(data, status=status.HTTP_201_CREATED)
        else:
            # Обработка случая, когда платеж не прошел
            return Response(
                {"message": "Проблема на стороне банка"},
                status=status.HTTP_404_NOT_FOUND,
            )

    def retrieve(self, request, *args, **kwargs):
        # Извлекаем идентификаторы сервиса и тарифного плана из URL
        service_id = self.kwargs.get('service_id')
        tariff_kind_id = self.kwargs.get('tariff_kind_id')

        # Обработка GET запроса для получения данных перед оплатой
        if not request.user.is_authenticated:
            return Response(
                {"error": "Необходима аутентификация пользователя"},
                status=status.HTTP_401_UNAUTHORIZED
            )
        # Получение сервиса и тарифа
        service = get_object_or_404(Service, pk=service_id)
        tariff_kind = get_object_or_404(TariffKind, pk=tariff_kind_id)

        # Формирование данных для ответа
        payment_data = {
            'service': service.id,
            'tariff_kind': tariff_kind.id,
            # 'user': request.user.id,
            'accept_rules': True,
            'total': tariff_kind.cost_total,
            'phone_number': request.user.phone_number,
            # 'is_trial': True
        }
        payment_instance = Payment(service=service, tariff_kind=tariff_kind)
        serializer = self.serializer_class(instance=payment_instance, context={'request': request})
        is_trial = serializer.get_is_trial(payment_instance)
        # Добавляем is_trial в данные для ответа
        payment_data['is_trial'] = is_trial
        return Response(payment_data)

    # def handle_invalid_data(self, serializer_errors):
    #     # Обработка невалидных данных
    #     error_messages = {"errors": serializer_errors}
    #     return Response(error_messages, status=status.HTTP_400_BAD_REQUEST)


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

    def get_queryset(self):
        user = self.request.user
        return Payment.objects.filter(user=user)


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
