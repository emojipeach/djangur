# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import codecs
import logging
import os

from time import time
from uuid import uuid4

from django.contrib import messages
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from django.http import Http404
from django.shortcuts import render
from django.urls import reverse

from imageapp.forms import ImageUploadForm
from imageapp.models import ImageUpload
from imageapp.settings import MODERATION_COUNTER_RESET
from imageapp.settings import MODERATION_THRESHOLD
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
    if current_image.reported >= MODERATION_THRESHOLD:

        messages.error(request, 'Image ({0}) awaiting moderation.'.format(identifier))

        return HttpResponseRedirect(reverse('imageapp:index'))
    # Lets check if the image has expired and is awaiting deletion
    if current_image.expiry_time < time() and current_image.expiry_time > current_image.uploaded_time:
        raise Http404("Page not found")

    context = {
        'current_image': current_image,
    }
    return render(request, 'imageapp/image.html', context)


def profile(request, username):
    """ Displays a user's profile."""
    current_user = User.objects.get(username=username)
    user_id = current_user.id
    images = ImageUpload.objects.filter(owner=user_id).order_by('-uploaded_time')
    context = {
        'images': images,
        'current_user': current_user,
        }
    return render(request, 'imageapp/user_profile.html', context)


def delete_image(request, identifier, deletion_password=''):
    """ View to delete an image, a correct deletion password must be passed in the url."""
    try:
        current_image = ImageUpload.objects.get(identifier=identifier)
    except Exception:
        raise Http404("Page not found")
    # Lets check the deletion password is correct
    if deletion_password == current_image.deletion_password():
        # If so we need to delete the instance and all associated files
        os.remove(current_image.image_file.path)
        os.remove(current_image.thumbnail.path)
        current_image.delete()

        messages.success(request, 'Image ({0}) deleted.'.format(identifier))

        return HttpResponseRedirect(reverse('imageapp:index'))
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

    messages.success(request, 'Image ({0}) reported.'.format(identifier))

    return HttpResponseRedirect(reverse('imageapp:image', args=[identifier]))


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

        messages.success(request, 'Previous image ({0}) deleted.'.format(identifier))

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
        current_image.reported = -MODERATION_COUNTER_RESET
        current_image.reported_first_time = 0
        current_image.save(update_fields=['reported', 'reported_first_time'])
        # TODO attribute this action to the mod responsible

        messages.success(request, 'Previous image ({0}) acceptable.'.format(identifier))

        return HttpResponseRedirect(reverse('imageapp:mod_queue'))
    else:
        raise Http404("Page not found")


def mod_queue(request):
    """ View gets 10 images above moderation_threshold and sort by the first time they were reported."""
    images_for_moderation = ImageUpload.objects.filter(
        reported__gte=MODERATION_THRESHOLD
        ).order_by('-reported_first_time')[:10]
    # Lets pick a random image from this list to show to moderator
    try:
        pick_an_image = int(int(codecs.encode(os.urandom(1), 'hex'), 16) / 255 * len(images_for_moderation))
        # Random number upto len(i_for_m)
        moderate = images_for_moderation[pick_an_image]
    except (ValueError, IndexError):
        messages.error(request, 'Moderation queue empty')

        return HttpResponseRedirect(reverse('imageapp:index'))

    context = {
        'moderate': moderate
    }
    return render(request, 'imageapp/mod_queue.html', context)
