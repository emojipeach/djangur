# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from re import search as regex_search
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import reverse
from uuid import uuid4
from time import strftime, localtime

from .forms import ImageUploadForm
from .models import ImageUpload

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

def index(request):
    if request.method == 'POST':
        form = ImageUploadForm(request.POST, request.FILES)
        if form.is_valid():
            new_image = form.save(commit=False)
            new_image.identifier = uuid4().hex
            new_image.save()
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

