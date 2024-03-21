from django.conf.urls import url
from django.urls import include, path
from rest_framework import routers

from api.views import (CustomUserViewSet, CategoryViewSet, ServiceViewSet,
                       HistoryViewSet,
                       CatalogViewSet,
                       SubscriptionViewSet,
                       AutoPaymentViewSet, PaymentViewSet, SellHistoryViewSet)

router_v1 = routers.DefaultRouter()
router_v1.register('users', CustomUserViewSet, basename='users')
router_v1.register(r'history', HistoryViewSet)
router_v1.register(r'categories', CategoryViewSet)
router_v1.register(r'services', ServiceViewSet)
router_v1.register(r'catalog', CatalogViewSet)
router_v1.register(r'payments', PaymentViewSet)
# может быть autopayments не понадобится, если прикрутить его к PaymentViewSet
router_v1.register(r'autopayments', AutoPaymentViewSet)
# может быть sell_history не понадобится, если прикрутить его к PaymentViewSet
router_v1.register(r'sell_history', SellHistoryViewSet)
# может быть subscriptions логичнее прикрутить к CatalogViewSet надо подумать
# (пример с избранным/корзиной покупок диплом)
router_v1.register(r'subscriptions', CustomUserViewSet,
                   basename='subscriptions')


urlpatterns = [
    # url(r'^auth/', include('djoser.urls')),
    # url(r'^auth/', include('djoser.urls.authtoken')),
    url(r'', include(router_v1.urls)),
    path(
        'catalog/<int:id>/subscriptions/',
        SubscriptionViewSet.as_view({'post': 'create', 'delete': 'delete'}),
        name='subscriptions',
    ),
]
