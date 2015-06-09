# fileserver-edx
Simple authenticated file server for edX that checks the athentication sessions of the user before serving the file. Written in python.

## Configuring edX
This file server checks for the required authentication levels for edX by means of session sharing among Django frameworks. However, edX LMS and CMS are not configured with session sharing when they are installed. We have to configure them to do so. 

### Sample setup
LMS: www.example.com
CMS: studio.example.com
fileserver-edx: filesecure.example.com
