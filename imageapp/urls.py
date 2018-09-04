# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.urls import path

from . import views

app_name = 'imageapp'

urlpatterns = [
    # Home page
    path('', views.index, name='index'),
    path('upload/', views.upload, name='upload'),
    path('upload_from_url/', views.upload_from_url, name='upload_from_url'),
    path('image/<str:identifier>/', views.image, name='image'),
    path('delete_image/<str:identifier>/<str:deletion_password>/', views.delete_image, name='delete_image'),
    path('mod_delete_image/<str:identifier>/<str:deletion_password>/', views.mod_delete_image, name='mod_delete_image'),
    path('mod_image_acceptable/<str:identifier>/<str:deletion_password>/', views.mod_image_acceptable, name='mod_image_acceptable'),
    path('report_image/<str:identifier>/', views.report_image, name='report_image'),
    path('mod_queue/', views.mod_queue, name='mod_queue'),
]