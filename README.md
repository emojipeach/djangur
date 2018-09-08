## An image hosting script written in Django/Python

[![Codacy Badge](https://api.codacy.com/project/badge/Grade/7e1b9453f54840ff8d219f170ce196b8)](https://www.codacy.com/app/emojipeach/djangur?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=emojipeach/djangur&amp;utm_campaign=Badge_Grade)

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
* Upload from URL
* Image ownership and user accounts
* Anon uploads
    
### Todo:
* Image profile pages
* User settings page
* PW change
* Unittests

### Maybe:
* Karma
* Comments
* Private messaging
* Categories
* Animate gif thumbnails 

### Deployment
* Debug = False
* Set secretkey
* Delete users/make_admin url and view
* makemigrations
* migrate