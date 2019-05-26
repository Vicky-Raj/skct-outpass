from django.db import models
from student.models import Student
from tutor.models import Tutor
from warden.models import Warden
from security.models import Security

class Outpass(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    req_date = models.DateTimeField(auto_now_add=True)
    tutor_status = models.CharField(max_length=10)
    accepted_tutor = models.ForeignKey(Tutor, on_delete=models.DO_NOTHING,blank=True,null=True)
    warden_status = models.CharField(max_length=10)
    accepted_warden = models.ForeignKey(Warden, on_delete=models.DO_NOTHING,blank=True,null=True)
    security_status = models.CharField(max_length=10)
    accepted_security = models.ForeignKey(Security, on_delete=models.DO_NOTHING,blank=True,null=True)
    reason = models.CharField(max_length=100)
    dep_date = models.DateTimeField()
    req_days = models.CharField(max_length=15)
    expired = models.BooleanField(default=False)
    emergency = models.BooleanField(default=False)
    tutors = models.ManyToManyField(Tutor,related_name='tutor_outpass')
    wardens = models.ManyToManyField(Warden,related_name='warden_outpass')


class OPRecord(models.Model):
    student = models.ForeignKey(Student, on_delete=models.DO_NOTHING)
    accepted_warden = models.ForeignKey(Warden, on_delete=models.DO_NOTHING)
    accepted_tutor = models.ForeignKey(Tutor, on_delete=models.DO_NOTHING)
    accepted_security = models.ForeignKey(Security, on_delete=models.DO_NOTHING)
    req_date = models.DateTimeField()
    dep_date = models.DateTimeField(auto_now_add=True)
    reason = models.CharField(max_length=100)
    req_days = models.CharField(max_length=15)
    in_time = models.DateTimeField(blank=True,null=True)
    tutors = models.ManyToManyField(Tutor, related_name='tutor_log')
    wardens = models.ManyToManyField(Warden, related_name='warden_log')
    emergency = models.BooleanField(default=False)

class OPRalias(models.Model):
    alias_no = models.CharField(max_length=5)
    opr = models.ForeignKey(OPRecord,on_delete=models.CASCADE)
    outpass = models.ForeignKey(Outpass,on_delete=models.CASCADE)


class OTP(models.Model):
    otp = models.CharField(max_length=5)
    outpass = models.ForeignKey(Outpass, on_delete=models.CASCADE)
