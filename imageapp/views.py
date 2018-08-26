# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.http import HttpResponseRedirect, Http404
from django.urls import reverse
from uuid import uuid4
from time import time

from .forms import ImageUploadForm
from .models import ImageUpload

def index(request):
    if request.method == 'POST':
        form = ImageUploadForm(request.POST, request.FILES)
        if form.is_valid():
            new_image = form.save(commit=False)
            new_image.identifier = uuid4().hex
            new_image.uploaded_time = time()
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
    
    if current_image.expiry_time() < time() and current_image.expiry_time() > current_image.uploaded_time:
        raise Http404("Page not found")
    
    absolute_file_url = request.build_absolute_uri(current_image.image_file.url)
    
    context = {
        'current_image': current_image,
        'absolute_file_url': absolute_file_url,
    }
    return render(request, 'imageapp/image.html', context)

