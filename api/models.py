import os
import re
import string
import random
from datetime import datetime 
from djongo import models
from django.conf import settings
from djongo.storage import GridFSStorage
from django.core.files.storage import FileSystemStorage
from django.dispatch import receiver

# storage instance
default_storage = FileSystemStorage()
grid_fs_storage = GridFSStorage(collection='media', base_url=''.join([settings.BASE_URL, 'media/']))

def facesave(instance, filename):
    today = datetime.now()

    path = 'face/'
    dt = str(today.strftime("%Y%m%d%H%M%S"))
    people = str(re.sub(r"\s+", "", instance.name.lower()))
    ext = "." + filename.split('.')[-1]
    randtext = ''.join(random.choice(string.ascii_letters) for i in range(15))
    filename_reformat = people + randtext + dt + ext
    return os.path.join(path, filename_reformat)

# people model
class People(models.Model):

    # field model
    name = models.CharField(max_length=200)
    face = models.ImageField(upload_to=facesave,storage=default_storage)

    def __str__(self):
        return self.name


@receiver(models.signals.post_delete, sender=People)
def auto_delete_file_on_delete(sender, instance, *args, **kwargs):
    if instance.face:
        if os.path.isfile(instance.face.path):
            os.remove(instance.face.path)

@receiver(models.signals.pre_save, sender=People)
def auto_delete_file_on_change(sender, instance, *args, **kwargs):
    if not instance.pk:
        return False

    try:
        old_file = People.objects.get(pk=instance.pk).face
    except People.DoesNotExist:
        return False

    new_file = instance.face
    if not old_file == new_file:
        if os.path.isfile(old_file.path):
            os.remove(old_file.path)