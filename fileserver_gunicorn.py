"""
gunicorn configuration file: http://docs.gunicorn.org/en/develop/configure.html

This file is created and updated by ansible, edit at your peril
"""
import multiprocessing

preload_app = True
timeout = 300
bind = "unix:/edx/var/fileserver/fileserver.sock"
pythonpath = "/edx/app/edxapp/fileserver"

workers = (multiprocessing.cpu_count()-1) * 2 + 2

