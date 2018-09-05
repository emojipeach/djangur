# -*- coding: utf-8 -*-
from __future__ import unicode_literals

""" Sets the quality % value used to save an image. Default = 75."""
image_quality_val = 5

""" Set the size of generated thumbnails (width, height)."""
thumb_size = (200, 200)

""" Set the available expiry options."""
expiry_choices = (
    (1, '24 hours'),
    (7, '7 days'),
    (30, '30 days'),
    (60, '60 days'),
    (180, '180 days'),
    (365, '1 year'),
    (-10, 'Never'),
    )

""" Sets the frequency at which image expiries are checked and images deleted in seconds."""
expiry_removal_frequency = 3600

""" Sets a number of reports above which an image becomes inaccessable and is added to the moderation queue for approval or deletion."""
moderation_threshold = 1

""" When an image is moderated the counter will need to reach this number again before it is submitted for reevaluation."""
moderation_counter_reset = 10

""" Allowed image formats (need to be upper case image formats recognised by pillow."""
allowed_image_formats = ['JPEG', 'GIF', 'PNG']