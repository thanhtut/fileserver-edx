# fileserver-edx
Simple authenticated file server for edX that checks the athentication sessions of the user before serving the file. Written in python. It uses django-sendfile package https://github.com/johnsensible/django-sendfile. This sendfile package allows efficent sending of large files via Apache X-Sendfile or Nginx X-Accel-Redirect. To install the package, activate virtualenv for the project if you use and run "pip install django-senfile"

## Configuring edX
This file server checks for the required authentication levels for edX by means of session sharing among Django frameworks. However, edX LMS and CMS are not configured with session sharing when they are installed. We have to configure them to do so. 

In order to use session sharing make the following changes and restart edX LMS and CMS.

Changes required
1. Make CMS run on port 80. Edit /edx/app/nginx/sites-enabled/cms and change "listen 10180 to listen 80". Run "sudo service nginx restart".

### Sample setup
* LMS: edxlocal
* CMS: studio.edxlocal
* fileserver-edx: filesecure.edxlocal

####Set up virtual hosts 
For testing add the following items to /etc/hosts (for Linux). For real deployment chang DNS settings.
	192.168.33.20   edxlocal
	192.168.33.20   studio.edxlocal


## Access Control
It allows three level of access control. The first one is public access. After that there is authenticated users access which is accessible to anyone logged in into the edX. Third one is staff only which is accessible only to the users designated as staff such as lecturers and admin staff.
