# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import logging
import os
import requests

from datetime import datetime
from datetime import timedelta
from hashlib import sha256
from io import BytesIO
from PIL import ExifTags
from PIL import Image
from time import localtime
from time import strftime
from time import time
from urllib.parse import urlparse

from django.contrib.auth.models import User
from django.core.files.base import ContentFile
from django.db import models

from imageapp.settings import ALLOWED_IMAGE_FORMATS
from imageapp.settings import EXPIRY_CHOICES
from imageapp.settings import IMAGE_QUALITY_VAL
from imageapp.settings import THUMB_SIZE

logging.basicConfig(level=logging.DEBUG, format=' %(asctime)s - %(levelname)s - %(message)s')


def image_path(instance, filename):
    """ Provides a path and unique filename."""
    new_folder = str(sha256(str(datetime.fromtimestamp(instance.uploaded_time).strftime("%d%m%Y").encode('utf-8')).encode('utf-8')).hexdigest())[2:8]
    new_filename = instance.identifier
    ext = filename.split('.')[-1].lower()
    if filename.split('.')[0] == 'thumbnail':
        return '{0}/{1}_thumb.{2}'.format(new_folder, new_filename, ext)
    else:
        return '{0}/{1}.{2}'.format(new_folder, new_filename, ext)


class ImageUpload(models.Model):
    identifier = models.CharField(max_length=32, primary_key=True)
    uploaded_time = models.FloatField()
    title = models.CharField(max_length=50, blank=True)
    image_file = models.ImageField(upload_to=image_path, blank=True)
    thumbnail = models.ImageField(upload_to=image_path, blank=True, editable=False)
    expiry_choice = models.IntegerField(choices=EXPIRY_CHOICES)
    expiry_time = models.FloatField()
    private = models.BooleanField()
    reported = models.IntegerField(default=0)
    reported_first_time = models.FloatField(default=0)
    img_url = models.CharField(max_length=255, blank=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.process_main_image():
            raise Exception('Not a valid image file')
        if not self.make_thumbnail():
            raise Exception('Problem making thumbnail')
        super(ImageUpload, self).save(*args, **kwargs)

    @staticmethod
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

    @staticmethod
    def file_type_check(file_type):
        """ Ensures only allowed files uploaded."""
        if file_type not in ALLOWED_IMAGE_FORMATS:
            raise ValueError('File type not allowed!')

    @staticmethod
    def reorientate_image(image):
        """ Respects orientation tags in exif data while disregarding and erasing the rest."""
        if hasattr(image, '_getexif'):  # only present in JPEGs
            for orientation in ExifTags.TAGS.keys():
                if ExifTags.TAGS[orientation] == 'Orientation':
                    break
            e = image._getexif()       # returns None if no EXIF data
            if e is not None:
                exif = dict(e.items())
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

    def filename(self):
        """ Returns just the image filename saved in the instance."""
        return os.path.basename(self.image_file.name)

    def upload_success_password(self):
        """ Gives a password used to show the upload success page which includes a deletion link."""
        return sha256(str(self.uploaded_time).encode('utf-8')).hexdigest()[0:6]

    def deletion_password(self):
        """ Provides a password used to confirm the user should be able to delete the image."""
        return sha256(str(self.uploaded_time).encode('utf-8')).hexdigest()[6:12]

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
        """ Provides a formatted timestamp for template use."""
        result = "Uploaded at " + strftime('%b. %d, %Y, %-I:%M %p', localtime(self.uploaded_time))
        return result

    def get_expiry_time(self):
        """ Provided the exact expiry time of an instance."""
        uploaded = datetime.fromtimestamp(self.uploaded_time)
        expiry = uploaded + timedelta(days=self.expiry_choice)
        result = expiry.timestamp()
        return result

    def formatted_expiry_delta(self):
        """ Provides a formatted expiry time delta used in templates."""
        et = self.expiry_time
        ut = self.uploaded_time
        if et < ut:
            return 'Never expires'
        now = time()
        td = et - now
        days, remainder = divmod(td, 86400)
        hours, remainder = divmod(remainder, 3600)
        minutes = remainder // 60
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

    def process_main_image(self):
        """ Process the main image for saving (accounting for orientation, animated gifs and disallowed file types)."""
        try:  # We dont want to overwrite a file if already saved
            if os.path.isfile(self.image_file.path):
                return True
        except ValueError:
            logging.info('image_file.path had no vaue set yet, gonna process image')
        if self.image_file:  # Check we have an image uploaded
            image = Image.open(self.image_file)
        elif self.img_url:  # Check we have a URL
            name = urlparse(self.img_url).path.split('/')[-1]
            response = requests.get(self.img_url)
            if response.status_code == 200:
                image = Image.open(BytesIO(response.content))
                file_type = image.format.upper()
                self.file_type_check(file_type)
                if self.image_is_animated_gif(image, file_type):
                    self.image_file.save(name, ContentFile(response.content), save=True)
                    return True
            else:
                raise Exception('Not a valid image URL')
        else:
            raise Exception('No Image File or URL provided')
        file_type = image.format.upper()
        self.file_type_check(file_type)
        try:
            image = self.reorientate_image(image)
        except Exception:
            logging.info('There was an error dealing with EXIF data when trying to reorientate')
        finally:
            if self.image_is_animated_gif(image, file_type):
                pass
                # Animated gifs are not processed before being saved
            else:
                temp_image = BytesIO()
                image.save(temp_image, file_type, quality=IMAGE_QUALITY_VAL)
                temp_image.seek(0)
                self.image_file.save(self.image_file.name, ContentFile(temp_image.read()), save=False)
                temp_image.close()
            return True

    def make_thumbnail(self):
        """ Makes and saves a thumbnail."""
        image = Image.open(self.image_file)
        try:
            if os.path.isfile(self.thumbnail.path):
                return True
        except ValueError:
            logging.info('thumbnail.path had no vaue set yet, gonna process image')
        file_type = image.format.upper()
        ext = self.filename().split('.')[-1].lower()
        thumbnail_placefolder = "thumbnail.{0}".format(ext)
        image.thumbnail(THUMB_SIZE, Image.ANTIALIAS)
        temp_thumb = BytesIO()
        image.save(temp_thumb, file_type, quality=IMAGE_QUALITY_VAL)
        temp_thumb.seek(0)
        self.thumbnail.save(thumbnail_placefolder, ContentFile(temp_thumb.read()), save=False)
        temp_thumb.close()
        return True
