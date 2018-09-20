# -*- coding: utf-8 -*-

""" Contains all url patterns for imageapp app."""

from __future__ import unicode_literals

from django.urls import path

from . import views
from users.views import my_profile as settings

app_name = 'imageapp'

urlpatterns = [
    # Home page
    path(
        '', views.index,
        name='index'
        ),
    # Upload page
    path(
        'upload/',
        views.upload,
        name='upload'
        ),
    # View an image
    path(
        'image/<str:identifier>/',
        views.image,
        name='image'
        ),
    # Delete an image
    path(
        'delete_image/<str:identifier>/<str:deletion_password>/',
        views.delete_image,
        name='delete_image'
        ),
    # Moderator delete an image
    path(
        'mod_delete_image/<str:identifier>/<str:deletion_password>/',
        views.mod_delete_image,
        name='mod_delete_image'
        ),
    # Moderator reset image reporting
    path(
        'mod_image_acceptable/<str:identifier>/<str:deletion_password>/',
        views.mod_image_acceptable,
        name='mod_image_acceptable'
        ),
    # Report an image
    path(
        'report_image/<str:identifier>/',
        views.report_image,
        name='report_image'
        ),
    # Moderator queue
    path(
        'mod_queue/',
        views.mod_queue,
        name='mod_queue'
        ),
    # User settings
    path(
        'profile/settings/',
        settings,
        name='settings'
        ),
    # User images
    path(
        'profile/<str:username>/',
        views.profile,
        name='profile'
        ),
]