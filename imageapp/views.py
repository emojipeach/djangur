# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import logging
import os

from time import time
from uuid import uuid4

from django.http import HttpResponseRedirect
from django.http import Http404
from django.shortcuts import render
from django.urls import reverse

from imageapp.forms import ImageUploadForm
from imageapp.models import ImageUpload

logging.basicConfig(level=logging.DEBUG, format=' %(asctime)s - %(levelname)s - %(message)s')

def index(request):
    if request.method == 'POST':
        form = ImageUploadForm(request.POST, request.FILES)
        if form.is_valid():
            new_image = form.save(commit=False)
            new_image.identifier = uuid4().hex
            new_image.uploaded_time = time()
            new_image.save()
            
            absolute_file_url = request.build_absolute_uri(new_image.image_file.url)
            
            context = {
                'current_image': new_image,
                'absolute_file_url': absolute_file_url,
                'attempted_upload_success_password': new_image.upload_success_password(),
            }
            
            return render(request, 'imageapp/image.html', context)
    else:
        form = ImageUploadForm()
    context = {
        'form': form,
    }
    return render(request, 'imageapp/index.html', context)

def image(request, identifier):
    try:
        current_image = ImageUpload.objects.get(identifier=identifier)
    except Exception:
        raise Http404("Page not found")
    
    if current_image.expiry_time() < time() and current_image.expiry_time() > current_image.uploaded_time:
        raise Http404("Page not found")
    
    absolute_file_url = request.build_absolute_uri(current_image.image_file.url)
    
    context = {
        'current_image': current_image,
        'absolute_file_url': absolute_file_url,
    }
    return render(request, 'imageapp/image.html', context)

def delete_image(request, identifier, deletion_password=''):
    try:
        current_image = ImageUpload.objects.get(identifier=identifier)
    except Exception:
        raise Http404("Page not found")
    
    if deletion_password == current_image.deletion_password():
        filename = current_image.filename
        os.remove(current_image.image_file.path)
        os.remove(current_image.thumbnail.path)
        current_image.delete()
        context ={
            'filename': filename,
        }
        return render(request, 'imageapp/image_deleted.html', context)
        
    else:
        raise Http404("Page not found")