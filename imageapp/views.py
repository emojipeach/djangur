# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import logging

from re import search as regex_search

from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import reverse
from uuid import uuid4
from time import strftime, localtime
from PIL import Image, ExifTags

from .forms import ImageUploadForm
from .models import ImageUpload
from .settings import image_quality_val

def get_folder_filename(instance):
    """ Returns a tuple containing folder and filename when given an image instance."""
    regex = r"^/img/(.+)/([^/]+)$"
    url = instance.image_file.url
    match = regex_search(regex, url)
    folder = match.group(1)
    filename = match.group(2)
    return (folder, filename)

def get_filesize(instance):
    size_bytes = instance.image_file.size
    if size_bytes > 1048576:
        result = "{0:.2f}".format(size_bytes / 1048576) + " MB"
    elif size_bytes > 1024:
        result = "{0:.0f}".format(size_bytes / 1024) + " KB"
    else:
        result = '{:,}'.format(size_bytes) + " Bytes"
    return result

def strip_exif_change_quality(instance):
    image = Image.open(instance.image_file.path)
    
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

#    image.thumbnail((THUMB_WIDTH , THUMB_HIGHT), Image.ANTIALIAS)
#    image.save(os.path.join(path,fileName))

    except Exception:
        logging.info('There was an error dealig with EXIF data when trying to deal with orientation')
    
    finally:
        image.save(instance.image_file.path, quality=image_quality_val)
        image.close()


def index(request):
    if request.method == 'POST':
        form = ImageUploadForm(request.POST, request.FILES)
        if form.is_valid():
            new_image = form.save(commit=False)
            new_image.identifier = uuid4().hex
            new_image.save()
            strip_exif_change_quality(new_image)
            return HttpResponseRedirect(reverse('imageapp:image', args=[new_image.identifier]))
    else:
        form = ImageUploadForm()
    context = {
        'form': form,
    }
    return render(request, 'imageapp/index.html', context)

def image(request, identifier):
    current_image = ImageUpload.objects.get(identifier=identifier)
    
    absolute_file_url = request.build_absolute_uri(current_image.image_file.url)
    
    filename = get_folder_filename(current_image)[1]
    
    filesize = get_filesize(current_image)
    
    date_time = strftime('%b. %d, %Y, %-I:%M %p', localtime(current_image.uploaded_time))
    
    context = {
        'filesize': filesize,
        'filename': filename,
        'current_image': current_image,
        'absolute_file_url': absolute_file_url,
        'date_time': date_time,
    }
    return render(request, 'imageapp/image.html', context)

