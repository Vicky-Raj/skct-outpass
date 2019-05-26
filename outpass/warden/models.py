from django.db import models
from django.contrib.auth.models import User



class Warden(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image = models.ImageField(default='default.jpg',upload_to='profile_img')
    device_id = models.CharField(max_length=200,blank=True,null=True)
    def __str__(self):
        return f'{self.user.username}'


