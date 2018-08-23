# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os.path

from django.db import models
from time import time
from PIL import Image
from io import BytesIO
from django.core.files.base import ContentFile
from datetime import datetime
from base64 import b64encode
from hashlib import md5


def directory_path(instance, filename):
    ext = filename.split('.')[-1].lower()
    new_folder = str(b64encode(md5(str(datetime.fromtimestamp(time()).strftime("%d%m%Y").encode('utf-8')).encode('utf-8')).hexdigest().encode('utf-8')))[2:8]
    new_filename = str(b64encode(str(instance.identifier).encode('utf-8')))[2:10]
    return '{0}/{1}.{2}'.format(new_folder, new_filename, ext)

def thumb_directory_path(instance, filename):
    ext = filename.split('.')[-1]
    new_folder = str(b64encode(md5(str(datetime.fromtimestamp(time()).strftime("%d%m%Y").encode('utf-8')).encode('utf-8')).hexdigest().encode('utf-8')))[2:8]
    new_filename = str(b64encode(str(instance.identifier).encode('utf-8')))[2:10]
    return '{0}/{1}_thumb.{2}'.format(new_folder, new_filename, ext)

class ImageUpload(models.Model):
    identifier = models.CharField(max_length=32, primary_key=True)
    uploaded_time = models.FloatField(unique=True, default=time)
    title = models.CharField(max_length=50, blank=True)
    image_file = models.ImageField(upload_to=directory_path)
    thumbnail = models.ImageField(upload_to=thumb_directory_path, blank=True, editable=False)
#    uploaded_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.make_thumbnail():
            # set to a default thumbnail
            raise Exception('Could not create thumbnail - is the file type valid?')
        super(ImageUpload, self).save(*args, **kwargs)
    
    def make_thumbnail(self):
        THUMB_SIZE = (160, 160)
        image = Image.open(self.image_file)
        image.thumbnail(THUMB_SIZE, Image.ANTIALIAS)
        
        thumb_name, thumb_extension = os.path.splitext(self.image_file.name)
        
        thumb_extension = thumb_extension.lower()

        thumb_filename = thumb_name + '_thumb' + thumb_extension

        if thumb_extension in ['.jpg', '.jpeg']:
            FTYPE = 'JPEG'
        elif thumb_extension == '.gif':
            FTYPE = 'GIF'
        elif thumb_extension == '.png':
            FTYPE = 'PNG'
        else:
            return False    # Unrecognized file type

        # Save thumbnail to in-memory file as StringIO
        temp_thumb = BytesIO()
        image.save(temp_thumb, FTYPE)
        temp_thumb.seek(0)

        # set save=False, otherwise it will run in an infinite loop
        self.thumbnail.save(thumb_filename, ContentFile(temp_thumb.read()), save=False)
        temp_thumb.close()

        return True

    
