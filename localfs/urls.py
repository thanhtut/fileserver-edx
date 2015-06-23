from django.conf.urls import url

from . import views
#from .views import download, download_list

urlpatterns = [
    url(r'^$', views.index, name='index'),
 #   url(r'^$', download_list),
 #   url(r'(?P<download_id>\d+)/$', download, name='download'),
    url(ur'^public/(?P<path>.*)$',views.public),
    url(ur'^user/(?P<path>.*)$',views.user),
    url(ur'^staff/(?P<path>.*)$',views.staff)

]

