from django.shortcuts import render,get_object_or_404,redirect
from django.views import View
from django.http import HttpResponse,JsonResponse
from .models import Student
import datetime
import pytz
import json
import random
from api.views import request_notification
import threading
from django.core.exceptions import PermissionDenied
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from warden.models import Warden
from home.models import Outpass
from django.utils import timezone
from django.contrib.auth.models import User
from django.contrib.auth import authenticate,login
from django.contrib.auth.mixins import UserPassesTestMixin,LoginRequiredMixin
from home.models import OTP

class StudentLoginView(View):
    template_name = 'home/login.html'
    def get(self, request):
        return render(request, self.template_name,{'student':True})
    def post(self, request):
        try:
            user = Student.objects.get(
                user=User.objects.get(email=request.POST.get('email'))
                ).user
        except:
            return render(request, self.template_name,
            {'student':True,
            'wrong':True,
            'email':request.POST.get('email'),
            })
        else:
            user = authenticate(request, 
            username=user.username, 
            password=request.POST.get('password')
            )
            if user is None:
                return render(request, self.template_name,
                {'student':True,
                'wrong':True,
                'email':request.POST.get('email'),
                })
            login(request,user)
            response =  redirect('student-home', pk=request.user.student.pk)
            response.set_cookie('role', 'student', max_age=60*60*24*365)
            return response

class StudentHomePage(UserPassesTestMixin,View):
    template_name = 'student/student_home.html'
    def test_func(self):
        try:
            student = self.request.user.student
        except:
            return False
        else:
            student = get_object_or_404(Student, pk=self.kwargs['pk'])
            return student.user.pk == self.request.user.pk
    def get(self, request,pk):
        return render(request, self.template_name)

class OutpassCreateView(LoginRequiredMixin,UserPassesTestMixin,View):
    template_name = 'student/outpass.html'
    def test_func(self):
        try:
            student = self.request.user.student
        except:
            return False
        else:
            student = get_object_or_404(Student, pk=self.kwargs['pk'])
            return student.user.pk == self.request.user.pk and student.outpass_set.count() == 0
    def get(self, request,pk):
        return render(request, self.template_name)
    def post(self, request,pk):
        date = request.POST.get('outDate').replace('/', ' ')
        tz = pytz.timezone('Asia/Kolkata')
        date = tz.localize(dt=datetime.datetime.strptime(date, r'%m %d %Y %I:%M %p'))
        now = tz.localize(dt=(datetime.datetime.now() - datetime.timedelta(minutes=5)))
        date_limit = tz.localize(dt=(datetime.datetime.now() + datetime.timedelta(days=3)))
        if date > now and date < date_limit:
            outpass = Outpass()
            outpass.student = request.user.student
            outpass.tutor_status = 'pending'
            outpass.warden_status = 'pending'
            outpass.security_status = 'pending'
            outpass.reason = request.POST.get('purpose')
            outpass.dep_date = date
            outpass.req_days = request.POST.get('noDays')
            outpass.save()
            for warden in request.user.student.wardens.all():
                outpass.wardens.add(warden)
            for tutor in request.user.student.tutors.all():
                outpass.tutors.add(tutor)
            outpass.save()
            th = threading.Thread(target=request_notification,args=(request.user.student,'tutor'))
            th.start()
            return redirect('student-home',pk=request.user.student.pk)
        else:
            return render(request,self.template_name,{'invalid_date':True})

class ProfileView(LoginRequiredMixin,View):
    template_name ="student/profile.html"
    def get(self,request,pk):
        student=get_object_or_404(Student,pk=pk)
        return render(request,self.template_name,{'student':student})

def get_otp():
    otp = str(random.randrange(10000,99999))
    otps= [otp.otp for otp in OTP.objects.all()]
    while otp in otps:
        otp = str(random.randrange(10000,99999))
    return otp


@require_POST
@csrf_exempt
def op_delete(request):
    outpass = get_object_or_404(Outpass, pk=json.loads(request.body).get('pk'))
    if request.user.student.pk != outpass.student.pk:
        raise PermissionDenied
    else:
        outpass.delete()
        return JsonResponse({'deleted':True})


@require_POST
@csrf_exempt
def gen_otp(request):
    op=get_object_or_404(Outpass,pk=json.loads(request.body).get('pk'))
    if  not op.tutor_status == 'accepted' and not op.warden_status == 'accepted' and not op.security_status == 'pending':
        raise PermissionDenied
    #Next check
    if not op.student.pk == request.user.student.pk:
        raise PermissionDenied
    if op.otp_set.count() >= 1:
        raise PermissionDenied
    else:
        otp = OTP(
            otp = get_otp(),
            outpass = op
            )
        otp.save()
        return JsonResponse({'created':True})

        # date = request.POST.get('outDate').replace('/', ' ')
        # aw_date = pytz.UTC.localize(dt=datetime.datetime.strptime(date, r'%m %d %Y %I:%M %p'))
        # tar_date = pytz.UTC.localize(datetime.datetime.now() + datetime.timedelta(days=3))
        # print(aw_date < tar_date)

