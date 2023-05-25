from djongo import models
from django.conf import settings
from djongo.storage import GridFSStorage

#GrifFSStorage instance
grid_fs_storage = GridFSStorage(collection='myfiles', base_url=''.join([settings.BASE_URL, 'myfiles/']))

# people model
class People(models.Model):
    name = models.CharField(max_length=200)
    face = models.ImageField(upload_to='face',storage=grid_fs_storage)

    def __str__(self):
        return self.name