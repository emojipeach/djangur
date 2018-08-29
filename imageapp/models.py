# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import logging
import os

from datetime import datetime
from datetime import timedelta
from hashlib import md5
from io import BytesIO
from PIL import ExifTags
from PIL import Image
from time import localtime
from time import strftime
from time import time

from django.core.files.base import ContentFile
from django.db import models

from imageapp.settings import expiry_choices
from imageapp.settings import image_quality_val
from imageapp.settings import thumb_size

logging.basicConfig(level=logging.DEBUG, format=' %(asctime)s - %(levelname)s - %(message)s')

def image_path(instance, filename):
    new_folder = str(md5(str(datetime.fromtimestamp(instance.uploaded_time).strftime("%d%m%Y").encode('utf-8')).encode('utf-8')).hexdigest())[2:8]
    new_filename = instance.identifier
    ext = filename.split('.')[-1].lower()
    if filename.split('.')[0] == 'thumbnail':
        return '{0}/{1}_thumb.{2}'.format(new_folder, new_filename, ext)
    else:
        return '{0}/{1}.{2}'.format(new_folder, new_filename, ext)

def image_is_animated_gif(image, image_format):
    """ Checks whether an image is an animated gif by trying to seek beyond the initial frame. """
    if image_format != 'GIF':
        return False
    try:
        image.seek(1)
    except EOFError:
        return False
    else:
        return True

def reorientate_image(image):
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
    return image

class ImageUpload(models.Model):
    identifier = models.CharField(max_length=32, primary_key=True)
    uploaded_time = models.FloatField()
    title = models.CharField(max_length=50, blank=True)
    image_file = models.ImageField(upload_to=image_path)
    thumbnail = models.ImageField(upload_to=image_path, blank=True, editable=False)
    expiry_choice = models.IntegerField(choices=expiry_choices)
    expiry_time = models.FloatField()
    private = models.BooleanField()

    def save(self, *args, **kwargs):
        if not self.strip_exif_make_thumb():
            raise Exception('Not a valid image (jpg, gif, png) file type')
        super(ImageUpload, self).save(*args, **kwargs)
    
    def filename(self):
        return os.path.basename(self.image_file.name)
    
    def upload_success_password(self):
        return md5(str(self.uploaded_time).encode('utf-8')).hexdigest()[0:6]
    
    def deletion_password(self):
        return md5(str(self.uploaded_time).encode('utf-8')).hexdigest()[6:12]
    
    def formatted_filesize(self):
        """ Returns a formatted string for use in templates from the image.size attribute provided in bytes."""
        size_bytes = self.image_file.size
        if size_bytes > 1048576:
            result = "Filesize: " + "{0:.2f}".format(size_bytes / 1048576) + " MB"
        elif size_bytes > 1024:
            result = "Filesize: " + "{0:.0f}".format(size_bytes / 1024) + " KB"
        else:
            result = "Filesize: " + '{:,}'.format(size_bytes) + " Bytes"
        return result
    
    def formatted_uploaded_time(self):
        result = "Uploaded at " + strftime('%b. %d, %Y, %-I:%M %p', localtime(self.uploaded_time))
        return result
    
    def get_expiry_time(self):
        uploaded = datetime.fromtimestamp(self.uploaded_time)
        expiry = uploaded + timedelta(days=self.expiry_choice)
        result = expiry.timestamp()
        return result
    
    def formatted_expiry_delta(self):
        et = self.expiry_time
        ut = self.uploaded_time
        if et < ut:
            return 'Never expires'
        now = time()
        td = et - now
        days, remainder = divmod(td, 86400)
        hours, remainder = divmod(remainder, 3600)
        minutes, seconds = divmod(remainder, 60)
        if int(days) == 1:
            days_string = 'day'
        else:
            days_string = 'days'
        if int(hours) == 1:
            hours_string = 'hour'
        else:
            hours_string = 'hours'
        if int(minutes) == 1:
            minutes_string = 'minute'
        else:
            minutes_string = 'minutes'
        if days > 7:
            return 'Expires in {0} {1}'.format(int(days), days_string)
        elif days > 1:
            return 'Expires in {0} {1} and {2} {3}'.format(int(days), days_string, int(hours), hours_string)
        else:
            return 'Expires in {0} {1} and {2} {3}'.format(int(hours), hours_string, int(minutes), minutes_string)
    
    def strip_exif_make_thumb(self):
        image = Image.open(self.image_file)
        
        file_type = image.format.upper()
        
        try:
            image = reorientate_image(image)
        except Exception:
            logging.info('There was an error dealing with EXIF data when trying to reorientate')
        finally:
            if image_is_animated_gif(image, file_type) == True:
                pass
                # Animated gifs are not processed before being saved
            else:
                temp_image = BytesIO()
                image.save(temp_image, file_type, quality=image_quality_val)
                temp_image.seek(0)
                self.image_file.save(self.image_file.name, ContentFile(temp_image.read()), save=False)
                temp_image.close()
            
            # TODO Evaluation and processing of animated gif thumbnails
                
            ext = self.filename().split('.')[-1].lower()
            thumbnail_placefolder = "thumbnail.{0}".format(ext)
            image.thumbnail(thumb_size, Image.ANTIALIAS)
            temp_thumb = BytesIO()
            image.save(temp_thumb, file_type, quality=image_quality_val)
            temp_thumb.seek(0)
            self.thumbnail.save(thumbnail_placefolder, ContentFile(temp_thumb.read()), save=False)
            temp_thumb.close()
 
            return True