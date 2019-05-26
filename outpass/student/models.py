from django.db import models
from django.contrib.auth.models import User
from tutor.models import Tutor
from warden.models import Warden

class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    reg_no = models.CharField(max_length=10)
    dep = models.CharField(max_length=10)
    room = models.CharField(max_length=8)
    batch = models.CharField(max_length=5,null=True,blank=True)
    tutors = models.ManyToManyField(Tutor)
    wardens = models.ManyToManyField(Warden)
    parent_no = models.CharField(max_length=10)
    student_no = models.CharField(max_length=10)
    image = models.ImageField(default='default.jpg',upload_to='profile_img')
    device_id = models.CharField(max_length=200,blank=True,null=True)
    def __str__(self):
        return f'{self.user.username}'