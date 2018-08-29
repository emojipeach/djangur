# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import logging
import os
import threading

from time import time
from uuid import uuid4

from django.db.models import F
from django.http import HttpResponseRedirect
from django.http import Http404
from django.shortcuts import render
from django.urls import reverse

from imageapp.forms import ImageUploadForm
from imageapp.models import ImageUpload
from imageapp.settings import expiry_removal_frequency

logging.basicConfig(level=logging.DEBUG, format=' %(asctime)s - %(levelname)s - %(message)s')

def delete_expired_images():
    now = time()
    images = ImageUpload.objects.filter(uploaded_time__lte=F('expiry_time'), expiry_time__lte=now)
    for image in images:
        filename = image.image_file.filename()
        os.remove(image.image_file.path)
        os.remove(image.thumbnail.path)
        image.delete()
        logging.info('deleted an expired image: {0}'.format(filename))

def launch_expired_image_remover():
    t = threading.Timer(expiry_removal_frequency, launch_expired_image_remover)
    t.start()
    delete_expired_images()

def index(request):
    images = ImageUpload.objects.filter(private=False).order_by('-uploaded_time')[:5]
    context = {'images': images}
    return render(request, 'imageapp/index.html', context)
    

def upload(request):
    if request.method == 'POST':
        form = ImageUploadForm(request.POST, request.FILES)
        if form.is_valid():
            new_image = form.save(commit=False)
            new_image.identifier = uuid4().hex
            new_image.uploaded_time = time()
            new_image.expiry_time = new_image.get_expiry_time()
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
    return render(request, 'imageapp/upload.html', context)

def image(request, identifier):
    try:
        current_image = ImageUpload.objects.get(identifier=identifier)
    except Exception:
        raise Http404("Page not found")
    
    if current_image.expiry_time < time() and current_image.expiry_time > current_image.uploaded_time:
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

launch_expired_image_remover()