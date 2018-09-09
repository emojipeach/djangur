# -*- coding: utf-8 -*-
from __future__ import unicode_literals

# Sets the quality % value used to save an image. Default = 75.
IMAGE_QUALITY_VAL = 5

# Set the size of generated thumbnails (width, height).
THUMB_SIZE = (200, 200)

# Set the available expiry options.
EXPIRY_CHOICES = (
    (1, '24 hours'),
    (7, '7 days'),
    (30, '30 days'),
    (60, '60 days'),
    (180, '180 days'),
    (365, '1 year'),
    (-10, 'Never'),
    )

# Sets the frequency at which image expiries are checked and images deleted in seconds.
EXPIRY_REMOVAL_FREQUENCY = 3600

# Sets a number of reports above which an image becomes inaccessable and is added to the moderation queue.
MODERATION_THRESHOLD = 1

# When an image is moderated the counter will need to reach this number again before it is submitted for reevaluation.
MODERATION_COUNTER_RESET = 10

# Allowed image formats (need to be upper case image formats recognised by pillow.
ALLOWED_IMAGE_FORMATS = ['JPEG', 'GIF', 'PNG']
