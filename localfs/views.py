# Create your views here.
from django.http import HttpResponse
from django.conf import settings
import importlib
from django.contrib.auth.models import User

def index(request):
    #sessionkey = request.session.session_key
    #keys=request.session.keys()
    session_key = request.COOKIES.get(settings.SESSION_COOKIE_NAME, None)
    if session_key:
        engine = importlib.import_module(settings.SESSION_ENGINE)
        session= engine.SessionStore(session_key)
        print(session.decode(""))
        #request.session = session
        #request.session.save()
	print(session_key)
        userid = session.get('_auth_user_id')
	print(session.get('_auth_user_id'))
        user = User.objects.get(pk=userid)
	dir(user)
	print(user)
        #| id | username | first_name | last_name | email                | password                                                                      | is_staff | is_active | is_superuser | last_login          | date_joined         |
        print(user.is_superuser)
        print(user.is_staff)
    response = HttpResponse("Hello, world. You're at the files index." )

    return response
