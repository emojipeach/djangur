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