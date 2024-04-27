from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from rest_framework import routers

from .views import (CategoriesViewSet, CategoryViewSet, CustomUserViewSet,
                    SellHistoryViewSet, ServiceViewSet, SubscribeViewSet,
                    SubscriptionPaymentViewSet,
                    SubscriptionViewSet)

router_v1 = routers.DefaultRouter()
router_v1.register(r"categories", CategoriesViewSet, basename="categories")
router_v1.register(r"users", CustomUserViewSet, basename="users")
router_v1.register(r"services", ServiceViewSet, basename="services")
router_v1.register(
    r"subscriptions", SubscriptionViewSet, basename="subscriptions"
)
router_v1.register(
    r"sell_history", SellHistoryViewSet, basename="sell_history"
)
# router_v1.register(r"subscribe", SubscribeViewSet, basename="subscribe")
router_v1.register(
    r"subscribe", SubscribeViewSet, basename="subscribe"
)
# router_v1.register(
#     r"subscription_payment",
#     SubscriptionPaymentViewSet,
#     basename="subscription_payment"
# )

urlpatterns = [
    path("", include(router_v1.urls)),
    path("catalog/", CategoryViewSet.as_view({"get": "list"}), name="catalog"),
    path(
        'subscription_payment/<int:service_id>/<int:tariff_kind_id>/',
        SubscriptionPaymentViewSet.as_view(
            {'get': 'retrieve', 'post': 'create'}
        ), name='subscription_payment'
    ),
    # path(
    #     "subscription_paid/",
    #     SubscriptionPaidView.as_view(),
    #     name="subscription_paid",
    # ),
    path(
        'subscriptions/<int:pk>/change_tariff/',
        SubscriptionViewSet.as_view({'patch': 'change_tariff'}),
        name='change_tariff',
    ),
    path(
        'subscriptions/<int:pk>/autopayment/',
        SubscriptionViewSet.as_view({'patch': 'autopayment'}),
        name='autopayment',
    ),
    path("", include("djoser.urls")),
    path("", include("djoser.urls.authtoken")),
    path("schema/", SpectacularAPIView.as_view(), name="schema"),
    path("schema/docs/", SpectacularSwaggerView.as_view(url_name="schema")),
]
