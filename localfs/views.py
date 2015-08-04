# Create your views here.
from django.http import HttpResponse
from django.http import HttpResponseForbidden
from django.http import HttpResponseNotFound
from django.conf import settings
import importlib
from django.contrib.auth.models import User
from sendfile import sendfile
import os.path

def registered_user_required(a_view):
    def _wrapped_view(request, *args, **kwargs):
        if __get_user(request):
            return a_view(request, *args, **kwargs)
        return HttpResponseForbidden()
    return _wrapped_view

def staff_required(a_view):
    def _wrapped_view(request, *args, **kwargs):
        if __get_user(request).is_staff:
            return a_view(request, *args, **kwargs)
        return HttpResponseForbidden()
    return _wrapped_view


def __get_user(request_obj):
    session_key = request_obj.COOKIES.get(settings.SESSION_COOKIE_NAME, None)
    engine = importlib.import_module(settings.SESSION_ENGINE)
    session= engine.SessionStore(session_key)
    userid = session.get('_auth_user_id')
    if userid:
        user = User.objects.get(pk=userid)
        return user
    return False


@registered_user_required
def index(request):
    #sessionkey = request.session.session_key
    #keys=request.session.keys()
    #response = HttpResponse("Hello, world. You're at the files index." )
    return HttpResponse("This simple file server with authentication. There is nothing useful here on its index page.")

def public(request,path):
    fileroot = settings.SENDFILE_ROOT
    filename = os.path.join(fileroot, 'public',path)
    if os.path.isfile(filename):
        return sendfile(request, filename)
    else:
        return HttpResponseNotFound('<h1>File not found</h1>')


@registered_user_required
def user(request,path):
    fileroot = settings.SENDFILE_ROOT
    filename = os.path.join(fileroot, 'user',path)
    if os.path.isfile(filename):
        return sendfile(request, filename)
    else:
        return HttpResponseNotFound('<h1>File not found</h1>')

def staff(request,path):
    fileroot = settings.SENDFILE_ROOT
    filename = os.path.join(fileroot, 'staff',path)
    #nginx backend do not require /staff path to be included
    if (settings.SENDFILE_BACKEND == 'sendfile.backends.nginx'):
        #Remove nginx-protected from path
        #nginx_path = path.replace("nginx-protected/","")
        filename = os.path.join(fileroot,  urllib.quote(path))

    if os.path.isfile(filename):
        return sendfile(request, filename)
    else:
        return HttpResponseNotFound('<h1>File not found</h1>'+filename +path)
