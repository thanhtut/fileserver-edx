from django.db import models

# Create your models here.

from django.db import models

from django.contrib.auth.models import User
from django.conf import settings
from django.core.files.storage import FileSystemStorage

sendfile_storage = FileSystemStorage(location=settings.SENDFILE_ROOT)

#it needs to support init, store, store_row and links_for functions
class FileDownload(models.Model):
    #users = models.ManyToManyField(User, blank=True)
    is_public = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    title = models.CharField(max_length=255)
    # files stored in SENDFILE_ROOT directory (which should be protected)
    file = models.FileField(upload_to='filedownload', storage=sendfile_storage)

    def is_user_allowed(self, user):
        return self.users.filter(pk=user.pk).exists()

    def __unicode__(self):
        return self.title

    @models.permalink
    def get_absolute_url(self):
        return ('filedownload', [self.pk], {})
