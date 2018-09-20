# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.auth import get_user_model
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin


User = get_user_model()


class CustomUserAdmin(UserAdmin):
    model = User
    list_display = ['username']
    fieldsets = (
        (None, {
            'fields': ('username', 'email', 'first_name', 'last_name', 'groups', 'pgp_key')
        }),
        ('Advanced options', {
            'classes': ('collapse',),
            'fields': ('password',),
        }),
    )

admin.site.register(User, CustomUserAdmin)