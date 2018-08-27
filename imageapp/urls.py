from django.urls import path

from . import views

app_name = 'imageapp'

urlpatterns = [
    # Home page
    path('', views.index, name='index'),
    path('image/<str:identifier>/<str:upload_success_password>/', views.image, name='image'),
    path('image/<str:identifier>/', views.image, name='image'),
    path('delete_image/<str:identifier>/<str:deletion_password>/', views.delete_image, name='delete_image'),
]