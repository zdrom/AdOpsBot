from django.urls import include, path
from . import views
from rest_framework import routers

router = routers.DefaultRouter()
router.register(r'creatives', views.CreativeViewSet)

app_name = 'creatives'
urlpatterns = [
    path('home/', views.save_creatives, name='index'),
    path('', include(router.urls)),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework'))
]