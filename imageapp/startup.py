# -*- coding: utf-8 -*-

""" Runs at startup (called by imageapp.views)."""

from __future__ import unicode_literals

import logging
import os
import threading

from time import time

from django.db.models import F

from imageapp.models import ImageUpload
from imageapp.settings import EXPIRY_REMOVAL_FREQUENCY

logging.basicConfig(level=logging.DEBUG, format=' %(asctime)s - %(levelname)s - %(message)s')


def delete_expired_images():
    """ This function selects all images which have an expiry set before now and deletes them permanently."""
    logging.info('Expired image cleanup started...')
    now = time()
    images = ImageUpload.objects.filter(uploaded_time__lte=F('expiry_time'), expiry_time__lte=now)
    for image in images:
        # lets delete the image file, thumbnail and instance
        filename = image.image_file.filename()
        os.remove(image.image_file.path)
        os.remove(image.thumbnail.path)
        image.delete()
        logging.info('deleted an expired image: {0}'.format(filename))
    logging.info('Expired image cleanup finished...')


def launch_expired_image_remover():
    """ This function runs the expired images delete function every hour (freq can be changed in settings)."""
    threads = threading.Timer(EXPIRY_REMOVAL_FREQUENCY, launch_expired_image_remover)
    threads.start()
    delete_expired_images()

launch_expired_image_remover()
