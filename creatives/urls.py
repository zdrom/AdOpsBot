from django.urls import include, path
from . import views

app_name = 'creatives'
urlpatterns = [
    path('bot/', views.bot, name='bot'),
    path('preview/', views.preview, name='preview'),
    path('get_click_through/', views.get_click_through, name='get_click_through'),
    path('add_macros/', views.add_macros, name='add_macros'),
    path('remove_blocking/', views.remove_blocking, name='remove_blocking'),
    path('take_screenshot/', views.take_screenshot, name='take_screenshot'),
]