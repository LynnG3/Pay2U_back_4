from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from rest_framework import routers

from .views import (
    CategoryViewSet,
    CustomUserViewSet,
    SellHistoryViewSet,
    ServiceViewSet,
    SubscribeView,
    SubscriptionPaidView,
    SubscriptionPaymentView,
    SubscriptionViewSet,
)

router_v1 = routers.DefaultRouter()
# router_v1.register(r'payments', PaymentViewSet)
router_v1.register(r"categories", CategoryViewSet)
router_v1.register(r"users", CustomUserViewSet, basename="users")
router_v1.register(r"services", ServiceViewSet, basename="services")
router_v1.register(
    r"subscriptions", SubscriptionViewSet, basename="subscriptions"
)
# сториз онбординг:
# router_v1.register(r'history', HistoryViewSet)
# история платежей юзера:
router_v1.register(r'sell_history', SellHistoryViewSet)

urlpatterns = [
    # url(r'^auth/', include('djoser.urls')),
    # url(r'^auth/', include('djoser.urls.authtoken')),
    path("", include(router_v1.urls)),
    path("", include("djoser.urls")),
    path("", include("djoser.urls.authtoken")),
    # path("services/", ServiceViewSet.as_view(
    #     {"get": "get_queryset"}
    # ), name="services"),
    # path("categories/", CategoryViewSet.as_view(
    #     {"get": "list"}
    # ), name="categories"),
    path("catalog/", ServiceViewSet.as_view(
        {"get": "list"}
    ), name="catalog"),
    # path(
    #     "catalog_new/",
    #     ServiceViewSet.as_view({"get": "get_queryset"}),
    #     name="catalog_new",
    # ),
    # path(
    #     "catalog_popular/",
    #     ServiceViewSet.as_view({"get": "list"}),
    #     name="catalog_popular",
    # ),
    # path(
    #     "catalog_category/<int:category_id>/",
    #     ServiceViewSet.as_view({"get": "list"}),
    #     name="catalog_category",
    # ),
    path("subscribe/", SubscribeView.as_view(), name="subscribe"),
    path(
        "subscription_payment/",
        SubscriptionPaymentView.as_view(),
        name="subscription_payment",
    ),
    path(
        "subscription_paid/",
        SubscriptionPaidView.as_view(),
        name="subscription_paid"
    ),
    path("", include("djoser.urls.authtoken")),
    path("schema/", SpectacularAPIView.as_view(), name="schema"),
    path("schema/docs/", SpectacularSwaggerView.as_view(url_name="schema")),
]
