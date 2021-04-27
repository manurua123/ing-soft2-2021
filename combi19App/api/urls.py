from django.urls import include, path
from rest_framework import routers
from . import views
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)


router = routers.DefaultRouter()
router.register(r'supplies', views.SuppliesViewSet)
router.register(r'driver', views.DriverViewSet)
router.register(r'bus', views.BusViewSet)
router.register(r'place', views.PlaceViewSet)
# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    path('api/', include(router.urls)),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh')
]