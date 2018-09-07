# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import logging
import os

from random import randint
from time import time
from uuid import uuid4

from django.http import HttpResponseRedirect
from django.http import Http404
from django.shortcuts import render
from django.urls import reverse

from imageapp.forms import ImageUploadForm
from imageapp.models import ImageUpload
from imageapp.settings import moderation_counter_reset
from imageapp.settings import moderation_threshold
# from imageapp.startup import delete_expired_images

logging.basicConfig(
    level=logging.DEBUG, format=' %(asctime)s - %(levelname)s - %(message)s'
    )


def index(request):
    """ Default index view which displays some recent images."""
    images = ImageUpload.objects.filter(private=False).order_by('-uploaded_time')[:5]
    context = {'images': images}
    return render(request, 'imageapp/index.html', context)


def upload(request):
    """ View for the image upload form."""
    if request.method == 'POST':
        form = ImageUploadForm(request.POST, request.FILES)
        if form.is_valid():
            new_image = form.save(commit=False)
            new_image.identifier = uuid4().hex
            new_image.uploaded_time = time()
            new_image.expiry_time = new_image.get_expiry_time()
            if request.user.is_authenticated:
                new_image.owner = request.user
            new_image.save()
            context = {
                'current_image': new_image,
                'attempted_upload_success_password': new_image.upload_success_password(),
            }
            
            return render(request, 'imageapp/image.html', context)
    else:  # Blank form initially
        form = ImageUploadForm()
    context = {
        'form': form,
    }
    return render(request, 'imageapp/upload.html', context)


def image(request, identifier):
    """ View which displays an image referenced by the identifier."""
    try:
        current_image = ImageUpload.objects.get(identifier=identifier)
    except Exception:
        raise Http404("Page not found")
    
    # Lets check if the image.reported field exceeds the moderation threshold
    if current_image.reported >= moderation_threshold:
        message = 'Image awaiting moderation'
        context = {
            'message': message,
        }
        return render(request, 'imageapp/result.html', context)
        
    # Lets check if the image has expired and is awaiting deletion
    if current_image.expiry_time < time() and current_image.expiry_time > current_image.uploaded_time:
        raise Http404("Page not found")
    
    context = {
        'current_image': current_image,
    }
    return render(request, 'imageapp/image.html', context)


def delete_image(request, identifier, deletion_password=''):
    """ View to delete an image, a correct deletion password must be passed in the url."""
    try:
        current_image = ImageUpload.objects.get(identifier=identifier)
    except Exception:
        raise Http404("Page not found")
    # Lets check the deletion password is correct
    if deletion_password == current_image.deletion_password():
        # If so we need to delete the instance and all associated files
        message = current_image.filename() + ' deleted'
        os.remove(current_image.image_file.path)
        os.remove(current_image.thumbnail.path)
        current_image.delete()
        context = {
            'message': message,
        }
        return render(request, 'imageapp/result.html', context)
        
    else:
        raise Http404("Page not found")


def report_image(request, identifier):
    """ View that increments the image.reported count and adds a timestamp to be used for the mod_queue."""
    try:
        current_image = ImageUpload.objects.get(identifier=identifier)
    except Exception:
        raise Http404("Page not found")
    # TODO should add some session checking to limt multiple reports
    current_image.reported += 1
    if current_image.reported_first_time == 0:
        current_image.reported_first_time = time()
    current_image.save(update_fields=['reported', 'reported_first_time'])
    
    message = 'Image has been reported for moderation'
    context = {
            'message': message,
        }
    return render(request, 'imageapp/result.html', context)


def mod_delete_image(request, identifier, deletion_password=''):
    """ View called from the mod_queue template which deletes an image and redirects back to the queue."""
    try:
        current_image = ImageUpload.objects.get(identifier=identifier)
    except Exception:
        raise Http404("Page not found")
    
    if deletion_password == current_image.deletion_password():
        os.remove(current_image.image_file.path)
        os.remove(current_image.thumbnail.path)
        current_image.delete()
        return HttpResponseRedirect(reverse('imageapp:mod_queue'))
        
    else:
        raise Http404("Page not found")


def mod_image_acceptable(request, identifier, deletion_password=''):
    """ View which resets the image.reported counter."""
    try:
        current_image = ImageUpload.objects.get(identifier=identifier)
    except Exception:
        raise Http404("Page not found")
    
    if deletion_password == current_image.deletion_password():
        current_image.reported = -moderation_counter_reset
        current_image.reported_first_time = 0
        current_image.save(update_fields=['reported', 'reported_first_time'])
        # TODO attribute this action to the mod responsible
        return HttpResponseRedirect(reverse('imageapp:mod_queue'))
    else:
        raise Http404("Page not found")
        

def mod_queue(request):
    """ View gets 10 images above moderation_threshold and sort by the first time they were reported."""
    images_for_moderation = ImageUpload.objects.filter(
        reported__gte=moderation_threshold
        ).order_by('-reported_first_time')[:10]
    # Lets pick a random image from this list to show to moderator
    try:
        moderate = images_for_moderation[randint(0, len(images_for_moderation) - 1)]
    except ValueError:
        message = 'Moderation queue empty'
        context = {
                'message': message,
            }
        return render(request, 'imageapp/result.html', context)
        
    context = {
        'moderate': moderate
    }
    return render(request, 'imageapp/mod_queue.html', context)