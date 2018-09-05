## An image hosting script written in Django/Python

Intended to be an open source privacy focussed image hosting script. Currently at an early stage.

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
* Report image implemented
* Mod queue implemented - needs protection with user login and mod group
* Upload from URL (should display 2 forms on one page)
    
### Todo:
* User account handling
* Anon uploads
* Refactor 2 upload forms
* Unittests

### Maybe:
* Karma
* Comments
* Categories
* Animate gif thumbnails 