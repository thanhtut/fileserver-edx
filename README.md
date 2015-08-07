# fileserver-edx
Simple authenticated file server for edX that checks the athentication sessions of the user before serving the file. Written in python. It uses django-sendfile package https://github.com/johnsensible/django-sendfile. This sendfile package allows efficent sending of large files via Apache X-Sendfile or Nginx X-Accel-Redirect. To install the package, activate virtualenv for the project if you use and run "pip install django-sendfile"

##Installing django-sendfile
It can be done simply by activating the virtual environment to use and running pip install
    sudo su edxapp -s /bin/bash
    cd ~
    source edxapp_env
    pip install dango-sendfile
    exit

## Configuring edX
###Enabling session sharing

This file server checks for the required authentication levels for edX by means of session sharing among Django applications. However, edX LMS and CMS are not configured with session sharing when they are installed. We have to configure them to do so. 

In order to use session sharing make the following changes and restart edX LMS and CMS.

Changes required
1. Make CMS run on port 80. Edit /edx/app/nginx/sites-enabled/cms and change "listen 10180 to listen 80". Run "sudo service nginx restart".
2. Session sharing can de done by simply changing the SESSION_COOKIE_DOMAIN configuration in the following places  

    /edx/app/edxapp/lms.env.json 

    /edx/app/edxapp/cms.env.json 

 
Make sure that the SESSION_COOKIE_NAME is the same for both configurations. (If it's already the same it doesn't have to be changed) 

"SESSION_COOKIE_DOMAIN": ".edxlocal.com",  "SESSION_COOKIE_NAME": "sessionid", 

For example, studio.asianux.academy and asianux.academy. The session cookie domain will be ".asianux.academy" 

In order to make sure it works with other extension of ours, add the "SESSION_ENGINE" configuration line at the end of the configuration file 

    "ZENDESK_URL": "",
    "SESSION_ENGINE": "django.contrib.sessions.backends.cached_db" 
    }  


### Sample setup (not necessary for live system. Add DNS record instead)
* LMS: edxlocal
* CMS: studio.edxlocal
* fileserver-edx: filesecure.edxlocal

####Set up virtual hosts (not necessary for live system. Add DNS record instead)
For testing add the following items to /etc/hosts (for Linux). For real deployment chang DNS settings.
	192.168.33.20   edxlocal
	192.168.33.20   studio.edxlocal
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

##Deploying fileserver edx.

Deploying the fileserver can be done in the same way as edX handles deployment of apps such as forum. The deployment makes use of gunicorn and nginx. The management of the gunicorn WSGI processes for the application can be achieved using supervisor. Deployment can be done in the following steps

+ Check out fileserveredx.
+ Configuring nginx
+ Configuring supervisor

### 1. Checking out file server
Get the fileserver code by checking out edx repository.

    git clone https://github.com/thanhtut/fileserveredx.git
	

### 2. Adding fileserveredx and patch to edx 
Moved all the contents checked out diretory to "/edx/app/edxapp/fileserver/". And copy the ./edx_patch/instructor_task/models.py file to /edx/app/edxapp/edx-platform/lms/djangoapps/instructor_task/models.py

### 3. Creating required folders
The file server require two folders to be crated. The first one is the folder for filestorage and the second one is the folder for gunicorn socket. 

    sudo mkdir /edx/files
    sudo mkdir /edx/files/staff
    sudo chown -R www-data:www-data /edx/files
    sudo mkdir /edx/var/fileserver
    sudo chown -R www-data:www-data /edx/var/fileserver
    
    

### 4. Configuring supervisor 
By adding a supervisor configuration file we can launch our fileserver or restart it in a similar way to how edx apps can be restarted. Do the follwing in order to add supervisor script for file server\

    cd ~/fileserveredx
    sudo cp ./config_files/supervisor/fileserver.conf /edx/app/supervisor/conf.d/
    sudo chown -R supervisor:www-data /edx/app/supervisor/conf.d/fileserver.conf
    sudo service supervisor restart
    
After that you can run the following command to start fileserver

    sudo /edx/bin/supervisorctl restart fileserver
    sudo /edx/bin/supervisorctl status 
    
### 5. Configuring nginx 
After supervisor has been configured, the fileserver application will be listening for connections at at unix socket at /edx/var/fileserver/fileserver.sock. Next step is to make it available through nginx. 

Make sure all that necessary hosts file or DNS is configured to redirect "files.[example site].org" to your server. After that copy "config_files/fileserver" to "/edx/app/nginx/sites-available/fileserver". After that create a symbolic to nginx site enabled folder. It can be done as follows. 


     sudo ln -s /edx/app/nginx/sites-available/fileserver /etc/nginx/sites-enabled/fileserver
     chown www-data:www-data /etc/nginx/sites-enabled/fileserver
     sudo service nginx restart

Try creating a report and download the files.
	
## Access Control
It allows three level of access control. The first one is public access. After that there is authenticated users access which is accessible to anyone logged in into the edX. Third one is staff only which is accessible only to the users designated as staff such as lecturers and admin staff.







#Giberish Warning I will remove them later

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

