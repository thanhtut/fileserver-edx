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

###Patching edx-platform
It requires new storage class to the LMS models. It has to be done here " edx-platform/lms/djangoapps/instructor_task/models.py". 

The settings for storage options has to be updated as well. The places to update is "/edx/app/edxapp/lms.env.json"

    "GRADES_DOWNLOAD": {
        "BUCKET": "edx-grades",
        "ROOT_PATH": "/edx/files/staff/",
        "STORAGE_TYPE": "simplefileserver",
        "ROOT_URL":"http://files.edxlocal.com/localfs/"
    },
Make sure the folder value for "ROOT_PATH" has the write permisson for the user www-data.


## Access Control
It allows three level of access control. The first one is public access. After that there is authenticated users access which is accessible to anyone logged in into the edX. Third one is staff only which is accessible only to the users designated as staff such as lecturers and admin staff.

##Deploying fileserver edx.
Deploying the fileserver can be done in the same way as edX handles deployment of apps such as forum. The deployment makes use of gunicorn and nginx. The management of the gunicorn processes for the application can be achieved using supervisor.

edX supervisor script is as follows 
	sudo -u www-data /edx/app/supervisor/venvs/supervisor/bin/supervisorctl -c /edx/app/supervisor/supervisord.conf $*

The supervisor files includes all the config files under "/edx/app/supervisor/conf.d/*.conf". The list of the files currently are 
- analytics_api.conf
- cms.conf
- edx_notes_api.conf
- insights.conf
- notifier-celery-workers.conf
- workers.conf  
- xqueue_consumer.conf
- certs.conf
- edxapp.conf
- forum.conf
- lms.conf
- notifier-scheduler.conf
- xqueue.conf

Forum.conf contains the following content
	[program:forum]
	command=/edx/app/forum/forum-supervisor.sh
	priority=999
	user=www-data
	stdout_logfile=/edx/var/log/supervisor/%(program_name)s-stdout.log
	stderr_logfile=/edx/var/log/supervisor/%(program_name)s-stderr.log
	killasgroup=true
	stopasgroup=true
	stopsignal=QUIT

The file /edx/app/forum/forum-supervisor.sh contailns the following scripts that run the gunicorn for forum.
	#!/bin/bash
	
	source /edx/app/forum/forum_env
	cd /edx/app/forum/cs_comments_service
	
	/edx/app/forum/.gem/bin/unicorn -c config/unicorn.rb
	
The gunicorn config for forum contains

	require 'tmpdir'
	worker_processes Integer(ENV['WORKER_PROCESSES'] || 4)
	timeout 25
	preload_app true
	data_dir = ENV['DATA_DIR'] || Dir.tmpdir
	listen "unix:#{data_dir}/forum.sock", :backlog => 512
	pid "#{data_dir}/forum_unicorn.pid"
	
	after_fork do |server, worker|
	  ::Mongoid.default_session.disconnect
	end
	
	
	
Finally the nginx configuration for the forum that connects to a socket contains

	upstream forum_app_server {
	  server unix:/edx/var/forum/forum.sock fail_timeout=0;
	}
	
	server {
	
	  server_name forum.*;
	  listen 18080 ;
	  client_max_body_size 1M;
	  keepalive_timeout 5;
	
	  location / {
	    try_files $uri @proxy_to_app;
	  }
	
	
	location @proxy_to_app {
	        proxy_set_header X-Forwarded-Proto $scheme;
	    proxy_set_header X-Forwarded-Port $server_port;
	    proxy_set_header X-Forwarded-For $remote_addr;
	        proxy_set_header Host $http_host;
	
	    proxy_redirect off;
	    proxy_pass http://forum_app_server;
	  }
	}


The fileserveredx app will also work in the similar fashion. Add nginx configuratin for fileserver in "/edx/app/nginx/sites-available/fileserver".

Activate the virtual enviroment and install after that run gunicorn test by entering
	gunicorn fileserveredx.wsgi:application --bind unix:/edx/var/fileserver/fileserver.sock -w4
Then create a file named fileserver in /edx/app/nginx/site-available/fileserver with the following content

	upstream fileserver {
	  server unix:/edx/var/fileserver/fileserver.sock fail_timeout=0;
	}
	
	server {
	
	  listen 80 ;
	
	  server_name files.*;
	#  server_name ~^((stage|prod)-)?files.*;
	
	
	  location / {
	    try_files $uri @proxy_to_app;
	  }
	
	
	location @proxy_to_app {
	        proxy_set_header X-Forwarded-Proto $scheme;
	    proxy_set_header X-Forwarded-Port $server_port;
	    proxy_set_header X-Forwarded-For $remote_addr;
	        proxy_set_header Host $http_host;
	
	    proxy_redirect off;
	    proxy_pass http://fileserver;
	  }
	}

	
After that create a symbolic link to enable the site

	sudo ln -s /edx/app/nginx/sites-available/fileserver /etc/nginx/sites-enabled/fileserver
	
And restart nginx.

Now fileserver should be running at files.[yourhostname]

