from django.urls import path

from . import views

app_name = 'imageapp'

urlpatterns = [
    # Home page
    path('', views.index, name='index'),
    path('image/<str:identifier>/', views.image, name='image'),
]