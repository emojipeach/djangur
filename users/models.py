# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import re

from django.contrib.auth.models import AbstractUser
from django.core import validators
from django.db import models
from django.utils.translation import ugettext_lazy as _


class CustomUser(AbstractUser):
    username = models.CharField(_('username'), max_length=30, unique=True,
    help_text=_('Required. 30 characters or fewer. Letters, numbers and ./-/_ characters'),
    validators=[
        validators.RegexValidator(re.compile('^[\w.-]+$'), _('Enter a valid username.'), _('invalid'))
    ])

    pgp_key = models.TextField(_("PGP public key"), blank=True)

    def __str__(self):
        return self.username
