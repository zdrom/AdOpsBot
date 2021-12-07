from django.urls import include, path
from . import views

app_name = 'creatives'
urlpatterns = [
    path('bot/', views.bot, name='bot'),
    path('preview/', views.preview, name='preview'),
    path('get_click_through/', views.get_click_through, name='get_click_through'),
    path('excel/', views.excel, name='excel'),

]