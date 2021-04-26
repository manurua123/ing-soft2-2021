from django.urls import include, path
from rest_framework import routers
from . import views
from django.conf.urls import url

router = routers.DefaultRouter()
router.register(r'supplies', views.SuppliesViewSet)
router.register(r'driver', views.DriverViewSet)
router.register(r'bus', views.BusViewSet)
router.register(r'place', views.PlaceViewSet)
router.register(r'route', views.RouteViewSet)
# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    path('api/', include(router.urls))
 ]