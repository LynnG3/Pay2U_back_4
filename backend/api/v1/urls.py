from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from rest_framework import permissions, routers

from .views import (  # CustomUserViewSet,; HistoryViewSet
    CategoryViewSet,
    CustomUserViewSet,
    ServiceViewSet,
    SubscriptionViewSet,
)

router_v1 = routers.DefaultRouter()
# router_v1.register('users', CustomUserViewSet, basename='users')
# router_v1.register(r'history', HistoryViewSet)
router_v1.register(r'categories', CategoryViewSet)
router_v1.register(r'services', ServiceViewSet)
router_v1.register(r'subscriptions', SubscriptionViewSet)
router_v1.register(r'users', CustomUserViewSet, basename='users')

# router_v1.register(r'payments', PaymentViewSet)
# # мб autopayments не понадобится, если прикрутить его к PaymentViewSet
# router_v1.register(r'autopayments', AutoPaymentViewSet)
# # мб sell_history не понадобится, если прикрутить его к PaymentViewSet
# router_v1.register(r'sell_history', SellHistoryViewSet)
# # мб subscriptions логичнее прикрутить к CatalogViewSet надо подумать
# # (пример с избранным/корзиной покупок диплом)
# router_v1.register(
#     r'subscriptions', CustomUserViewSet,basename='subscriptions'
# )


urlpatterns = [
    # url(r'^auth/', include('djoser.urls')),
    # url(r'^auth/', include('djoser.urls.authtoken')),
    path('', include(router_v1.urls)),
    path('', include('djoser.urls')),
    path('', include('djoser.urls.authtoken')),
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
    path('', include("djoser.urls.authtoken")),
    path('schema/', SpectacularAPIView.as_view(), name="schema"),
    path('schema/docs/', SpectacularSwaggerView.as_view(url_name="schema")),
    # path(
    #     'catalog/<int:id>/subscriptions/',
    #     SubscriptionViewSet.as_view({'post': 'create', 'delete': 'delete'}),
    #     name='subscriptions',
    # ),
]
