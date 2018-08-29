## A (very alpha) image hosting script written in Django/Python

Intended to be an open source privacy focussed image hosting script. Currently at a very early stage.

### Implemented:
* Basic upload form
* Basic image view
* Basic index with recent (non-private) images
* Image filename unique and unguessable
* EXIF stripping with orientation correction for jpegs
* Make thumbnails
* Image expiry with image delete script running hourly by default
* 'Copy' buttons
* Display filesize and expiry delta
* Accepts animated gifs (thumbnail not animated currently)
* Image privacy option
* Added some upload form defaults
* Added image deletion link and view with basic success template
    
### Todo:
* Image reporting / moderation
* 
* Function basic documentation
* Unittests
* 
* User account handling
* Anon uploads
* Upload from URL

### Maybe:
* Karma
* Decay
* Categories
* Animate gif thumbnails 