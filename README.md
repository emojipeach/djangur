## An image hosting script written in Django/Python

[![Codacy Badge](https://api.codacy.com/project/badge/Grade/7e1b9453f54840ff8d219f170ce196b8)](https://www.codacy.com/app/emojipeach/djangur?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=emojipeach/djangur&amp;utm_campaign=Badge_Grade)

Intended to be an open source privacy focussed image hosting script. 

### Features:
* Based on Django
* Upload from local files or URLs
* Private image option (Image will only displayed if full URL known and not linked anywhere else on the site)
* Image filename unique and unguessable (based on UUID4)
* EXIF stripping with orientation correction for jpegs
* Image expiry date can be specified with expired image cleanup script set to run hourly by default
* Image deletion link displayed on first upload to anonymous users but not subsequently
* Image deletion link available to logged in users when viewing their own files
* Image reporting system
* Moderation queue (create 'moderators' group and add a user to this to allow them to moderate)
* User accounts and ability to edit their own data
* Private messaging 
    
### Todo:
* Unittests
* Banned usernames (settings, admin, anonymous, profile)

### Maybe:
* Comments
* Categories
* Voting
* Animate gif thumbnails 

### Deployment
* set Debug = False
* set secured secret key
* makemigrations
* migrate
* uncomment cleanup/startup imports in pmessaging.views and imageapp.views. This needs to be done after migrate is run.
* create 'moderators' group