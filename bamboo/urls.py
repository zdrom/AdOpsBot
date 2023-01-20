from django.urls import include, path
from . import views

app_name = 'bamboo'
urlpatterns = [
    path('assign_coverage/', views.assign_coverage, name='assign_coverage'),
]
