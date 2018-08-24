## A (very alpha) image hosting script written in Django/Python

Intended to be an open source privacy focussed image hosting script. Currently at a very early stage.

Implemented:
    Basic upload form
    Basic image view
    Image filename unique and unguessable
    EXIF stripping with orientation correction for jpegs
    Make thumbnails
    Image expiry (needs file delete script)
    'Copy' buttons (needs js)
    Display filesize
    
Todo:
    Handle gifs outside PIL
    Function basic documentation
    Unittests
    Animate gif thumbnails (will need pillow) as described here:
        https://github.com/python-pillow/pillow-scripts/blob/master/Scripts/gifmaker.py
    User account handling
    Anon uploads
    Delete image link with upload 'success' page
    Privacy checkbox
    Image reporting / moderation
    Main view with recent (non-private) uploads

Maybe:
    Karma
    Decay
    Categories