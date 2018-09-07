# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django import forms
from .models import ImageUpload

class ImageUploadForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(ImageUploadForm, self).__init__(*args, **kwargs)
        self.fields['private'].initial  = True
        self.fields['expiry_choice'].initial = -10
    
    class Meta:
        model = ImageUpload
        fields = (
        'title',
        'image_file',
        'img_url',
        'expiry_choice',
        'private',
        )