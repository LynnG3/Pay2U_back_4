from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from rest_framework import routers

from .views import CategoryViewSet  # CustomUserViewSet,; HistoryViewSet
from .views import (CustomUserViewSet, ServiceViewSet, SubscribeView,
                    SubscriptionPaidView, SubscriptionPaymentView,
                    SubscriptionViewSet)

router_v1 = routers.DefaultRouter()
# router_v1.register(r'autopayments', AutoPaymentViewSet)
router_v1.register(r'categories', CategoryViewSet)
router_v1.register(r'users', CustomUserViewSet, basename='users')
# router_v1.register(r'history', HistoryViewSet)
# # мб sell_history не нужен, если прикрутить его к SubscriptionPaymentView
# router_v1.register(r'sell_history', SellHistoryViewSet)
router_v1.register(r'services', ServiceViewSet)
router_v1.register(r'subscriptions', SubscriptionViewSet)


urlpatterns = [
    # url(r'^auth/', include('djoser.urls')),
    # url(r'^auth/', include('djoser.urls.authtoken')),
    path('', include(router_v1.urls)),
    path('', include('djoser.urls')),
    path('', include('djoser.urls.authtoken')),
    path(
        'services/', ServiceViewSet.as_view({'get': 'list'}), name='services'
    ),
    path(
        'categories/', CategoryViewSet.as_view({'get': 'list'}),
        name='categories'
    ),
    path('catalog/', ServiceViewSet.as_view({'get': 'list'}), name='catalog'),
    path(
        'catalog_new/',
        ServiceViewSet.as_view({'get': 'list'}),
        name='catalog_new',
    ),
    path(
        'catalog_popular/',
        ServiceViewSet.as_view({'get': 'list'}),
        name='catalog_popular',
    ),
    path(
        'catalog_category/<int:category_id>/',
        ServiceViewSet.as_view({'get': 'list'}),
        name='catalog_category',
    ),
    path('subscribe/', SubscribeView.as_view(), name='subscribe'),
    path(
        'subscription_payment/', SubscriptionPaymentView.as_view(),
        name='subscription_payment'
    ),
    path(
        'subscription_paid/', SubscriptionPaidView.as_view(),
        name='subscription_paid'
    ),
    path('', include("djoser.urls.authtoken")),
    path('schema/', SpectacularAPIView.as_view(), name="schema"),
    path('schema/docs/', SpectacularSwaggerView.as_view(url_name="schema")),
]
