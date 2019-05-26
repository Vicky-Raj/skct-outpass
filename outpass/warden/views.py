from django.shortcuts import render,get_object_or_404,redirect
from django.views import View
from .models import Warden
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.core.exceptions import PermissionDenied
import json
from api.views import status_notification
import threading
import pytz
import datetime
from api.views import get_otp
from home.models import Outpass,OPRecord,OTP
from django.http import JsonResponse
from django.contrib.auth.models import User
from django.contrib.auth import login,authenticate
from django.contrib.auth.mixins import UserPassesTestMixin,LoginRequiredMixin
from django.core.exceptions import SuspiciousOperation
from django.conf import settings
from api.views import holiday_notify
from student.models import Student

class WardenLoginView(View):
    template_name = 'home/login.html'
    def get(self, request):
        return render(request, self.template_name,{'warden':True})
    def post(self, request):
        try:
            user = Warden.objects.get(
                user=User.objects.get(email=request.POST.get('email'))
                ).user
        except:
            return render(request, self.template_name,
            {'warden':True,
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
                {'warden':True,
                'wrong':True,
                'email':request.POST.get('email'),
                })
            login(request,user)
            respone = redirect('warden-home',pk=Warden.objects.get(user=user).pk)
            respone.set_cookie('role', 'warden',max_age=60*60*24*365)
            return respone

class WardenHomePage(LoginRequiredMixin, UserPassesTestMixin,View):
    template_name = 'warden/warden_home.html'
    def test_func(self):
        try:
            war = self.request.user.warden
        except:
            raise PermissionDenied
        else:
            warden = get_object_or_404(Warden, pk=self.kwargs['pk'])
            return warden.user.pk == self.request.user.pk
    def get(self, request,pk):
        outpasses = [outpass for outpass in request.user.warden.warden_outpass.all().order_by('dep_date')
                    if outpass.tutor_status == 'accepted' and outpass.warden_status == 'pending']
        return render(request, self.template_name,{'outpasses':outpasses})

class WardenLogView(LoginRequiredMixin, View):
    template_name = 'tutor/log.html'
    
    def get(self, request):
        try:
            war = request.user.warden
        except:
            raise PermissionDenied
        else:
            if request.GET.get('date') == None:
                return render(request,self.template_name,{'records':request.user.warden.warden_log.all().order_by('-dep_date')})
            else:
                date = request.GET.get('date').split('/')
                records = OPRecord.objects.filter(dep_date__year=date[2],dep_date__month=date[0],dep_date__day=date[1],wardens__in=[request.user.warden])
                return render(request,self.template_name,{'records':records})

class EmergencyOutpassView(LoginRequiredMixin,UserPassesTestMixin, View):
    template_name = 'warden/eoutpass.html'
    def test_func(self):
        try:
            warden = self.request.user.warden
        except:
            return False
        else:
            warden = get_object_or_404(Warden, pk=self.kwargs['pk'])
            return warden.user.pk == self.request.user.pk
    def get(self, request, pk):
        return render(request, self.template_name)
    def post(self, request, pk):
        try:
            user = User.objects.get(username=request.POST.get('rollno'))
        except:
            return render(request, self.template_name, {'noexists':True})
        else:
            if user.student.outpass_set.count() > 0:
                raise SuspiciousOperation
            tz = pytz.timezone('Asia/Kolkata')
            outpass = Outpass()
            outpass.student = user.student
            outpass.tutor_status = 'accepted'
            outpass.warden_status = 'accepted'
            outpass.accepted_tutor = user.student.tutors.first()
            outpass.accepted_warden = request.user.warden
            outpass.security_status = 'pending'
            outpass.reason = request.POST.get('purpose')
            outpass.dep_date = tz.localize(dt=datetime.datetime.now())
            outpass.req_days = request.POST.get('noDays')
            outpass.emergency = True
            outpass.save()
            for tutor in user.student.tutors.all():
                outpass.tutors.add(tutor)
            for warden in user.student.wardens.all():
                outpass.wardens.add(warden)
            outpass.save()
            otp = OTP(
                otp = get_otp(),
                outpass = outpass
            )
            otp.save()
            return redirect('warden-home',pk=request.user.warden.pk)

class HolidayOutpassView(LoginRequiredMixin, UserPassesTestMixin, View):
    template_name = 'warden/holiday_outpass.html'
    def test_func(self):
        try:
            warden = self.request.user.warden
        except:
            return False
        else:
            warden = get_object_or_404(Warden, pk=self.kwargs['pk'])
            return warden.user.pk == self.request.user.pk
    def get(self, request, pk):
        return render(request, self.template_name)
    def post(self, request, pk):
        tz = pytz.timezone('Asia/Kolkata')
        students = [student for student in request.user.warden.student_set.all() if student.outpass_set.count() == 0 
        and ((int(settings.YEAR) - int(student.batch.split('-')[0]))+1) == int(request.POST.get('year'))]
        for student in students:
            outpass = Outpass()
            outpass.student = student
            outpass.tutor_status = 'accepted'
            outpass.warden_status = 'accepted'
            outpass.accepted_tutor = student.tutors.first()
            outpass.accepted_warden = request.user.warden
            outpass.security_status = 'pending'
            outpass.reason = request.POST.get('purpose')
            outpass.dep_date = tz.localize(dt=datetime.datetime.now())
            outpass.req_days = "Holiday"
            outpass.save()
            for tutor in student.tutors.all():
                outpass.tutors.add(tutor)
            for warden in student.wardens.all():
                outpass.wardens.add(warden)
            outpass.save()
            otp = OTP(
                otp = get_otp(),
                outpass = outpass
            )
            otp.save()
        th = threading.Thread(target=holiday_notify,args=(request.user.warden,students))
        th.start()
        return redirect('warden-home',pk=request.user.warden.pk)

class WardenStudentsView(LoginRequiredMixin, View):
    template_name = 'tutor/student_log.html'
    def get(self, request):
        year = 1
        if not request.GET.get('rollno') == '' and request.GET.get('rollno'):
            students = Student.objects.filter(reg_no__istartswith=request.GET.get('rollno'),wardens__in=[request.user.warden]).order_by('pk')
            return render(request, self.template_name, {'students':students,'value':request.GET.get('rollno')})
        if request.GET.get('year'):
            year = request.GET.get('year')
        students = [student for student in request.user.warden.student_set.all().order_by('pk') 
            if ((int(settings.YEAR) - int(student.batch.split('-')[0]))+1) == int(year)]
        return render(request, self.template_name, {'students':students})
                
@require_POST
@csrf_exempt
def op_accept(request):
    try:
        war = request.user.warden
    except:
        raise PermissionDenied
    else:
        outpass = get_object_or_404(Outpass, pk=json.loads(request.body).get('pk'))
        if not request.user.warden in outpass.wardens.all():
            raise PermissionDenied
        elif not outpass.tutor_status == 'accepted' and not outpass.warden_status == 'pending':
            raise PermissionDenied
        else:
            outpass.accepted_warden = request.user.warden
            outpass.warden_status = 'accepted'
            outpass.save()
            th = threading.Thread(target=status_notification,args=(outpass.student,'accepted','warden'))
            th.run()
            return JsonResponse({'accepted':True})

@require_POST
@csrf_exempt
def op_reject(request):
    try:
        war = request.user.warden
    except:
        raise PermissionDenied
    else:
        outpass = get_object_or_404(Outpass, pk=json.loads(request.body).get('pk'))
        if not request.user.warden in outpass.wardens.all():
            raise PermissionDenied
        elif not outpass.tutor_status == 'accepted' and not outpass.warden_status == 'pending':
            raise PermissionDenied
        else:
            outpass.accepted_warden = request.user.warden
            outpass.warden_status = 'rejected'
            outpass.expired = True
            outpass.save()
            th = threading.Thread(target=status_notification,args=(outpass.student,'rejected','warden'))
            th.run()
            return JsonResponse({'rejected':True})
