# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os.path
import logging

from django.db import models
from time import time
from PIL import Image, ExifTags
from io import BytesIO
from django.core.files.base import ContentFile
from datetime import datetime
from hashlib import md5

from .settings import thumb_size, image_quality_val

def get_folder_filename_ext(instance, filename):
    new_folder = str(md5(str(datetime.fromtimestamp(time()).strftime("%d%m%Y").encode('utf-8')).encode('utf-8')).hexdigest())[2:8]
    new_filename = instance.identifier[0:16]
    ext = filename.split('.')[-1].lower()
    return (new_folder, new_filename, ext)


def image_path(instance, filename):
    path_tuple = get_folder_filename_ext(instance, filename)
    new_folder = path_tuple[0]
    new_filename = path_tuple[1]
    ext = path_tuple[2]
    return '{0}/{1}.{2}'.format(new_folder, new_filename, ext)

def thumb_path(instance, filename):
    path_tuple = get_folder_filename_ext(instance, filename)
    new_folder = path_tuple[0]
    new_filename = path_tuple[1]
    ext = path_tuple[2]
    return '{0}/{1}_thumb.{2}'.format(new_folder, new_filename, ext)

class ImageUpload(models.Model):
    identifier = models.CharField(max_length=32, primary_key=True)
    uploaded_time = models.FloatField(unique=True, default=time)
    title = models.CharField(max_length=50, blank=True)
    image_file = models.ImageField(upload_to=image_path)
    thumbnail = models.ImageField(upload_to=thumb_path, blank=True, editable=False)

    def save(self, *args, **kwargs):
        if not self.strip_exif_make_thumb():
            raise Exception('Not a valid image (jpg, gif, png) file type')
        super(ImageUpload, self).save(*args, **kwargs)
    
    def strip_exif_make_thumb(self):
        image = Image.open(self.image_file)
        
        image_name, image_extension = os.path.splitext(self.image_file.name)
        
        image_extension = image_extension.lower()
        if image_extension in ['.jpg', '.jpeg']:
            file_type = 'JPEG'
        elif image_extension == '.gif':
            file_type = 'GIF'
        elif image_extension == '.png':
            file_type = 'PNG'
        else:
            return False    # Unrecognized file type
        try:
            if hasattr(image, '_getexif'): # only present in JPEGs
                for orientation in ExifTags.TAGS.keys(): 
                    if ExifTags.TAGS[orientation]=='Orientation':
                        break 
                e = image._getexif()       # returns None if no EXIF data
                if e is not None:
                    exif=dict(e.items())
                    orientation = exif[orientation] 
                    if orientation == 2:
                        image = image.transpose(Image.FLIP_LEFT_RIGHT)
                    elif orientation == 3:
                        image = image.transpose(Image.ROTATE_180)
                    elif orientation == 4:
                        image = image.transpose(Image.FLIP_TOP_BOTTOM)
                    elif orientation == 5:
                        image = image.transpose(Image.FLIP_LEFT_RIGHT, Image.ROTATE_90)
                    elif orientation == 6:
                        image = image.transpose(Image.ROTATE_270)
                    elif orientation == 7:
                        image = image.transpose(Image.FLIP_TOP_BOTTOM, Image.ROTATE_90)
                    elif orientation == 8:
                        image = image.transpose(Image.ROTATE_90)
                    else:
                        pass
        except Exception:
            logging.info('There was an error dealing with EXIF data when trying to reorientate')
        finally:
            temp_image = BytesIO()
            image.save(temp_image, file_type, quality=image_quality_val)
            temp_image.seek(0)
            self.image_file.save(self.image_file.name, ContentFile(temp_image.read()), save=False)
            temp_image.close()
            image.thumbnail(thumb_size, Image.ANTIALIAS)
            temp_thumb = BytesIO()
            image.save(temp_thumb, file_type)
            temp_thumb.seek(0)
            self.thumbnail.save(self.image_file.name, ContentFile(temp_thumb.read()), save=False)
            temp_thumb.close()
            
            return True