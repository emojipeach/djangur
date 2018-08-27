## A (very alpha) image hosting script written in Django/Python

Intended to be an open source privacy focussed image hosting script. Currently at a very early stage.

### Implemented:
* Basic upload form
* Basic image view
* Image filename unique and unguessable
* EXIF stripping with orientation correction for jpegs
* Make thumbnails
* Image expiry (still needs file delete script)
* 'Copy' buttons
* Display filesize and expiry delta
* Accepts animated gifs (thumbnail not animated currently)
* Image privacy checkbox
* Added some upload form defaults
* Added image deletion link and view with basic success template
    
### Todo:
* Main view with recent (non-private) uploads
* Image reporting / moderation
* 
* Function basic documentation
* Unittests
* 
* User account handling
* Anon uploads
* 
* Animate gif thumbnails (will need pillow) as described here: https://github.com/python-pillow/pillow-scripts/blob/master/Scripts/gifmaker.py

### Maybe:
* Karma
* Decay
* Categories