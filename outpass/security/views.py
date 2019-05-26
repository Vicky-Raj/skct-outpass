from django.shortcuts import render, redirect,get_object_or_404
from django.views import View
from home.models import OPRecord,OPRalias
from api.views import get_record_no
from .models import Security
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from home.models import Outpass
from django.http import JsonResponse
from django.core.exceptions import PermissionDenied
import json
from home.models import OTP
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User
from django.contrib.auth import authenticate,login
from django.http import HttpResponse
from django.core.exceptions import SuspiciousOperation
import pytz
import datetime


class SecurityLoginView(View):
    template_name = 'home/login.html'
    def get(self, request):
        return render(request, self.template_name,{'security':True})
    def post(self, request):
        try:
            user = Security.objects.get(
                user=User.objects.get(email=request.POST.get('email'))
                ).user
        except:
            return render(request, self.template_name,
            {'security':True,
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
                {'security':True,
                'wrong':True,
                'email':request.POST.get('email'),
                })
            login(request,user)
            response =  redirect('sec-home', pk=user.security.pk)
            response.set_cookie('role', 'security',max_age=60*60*24*365)
            return response

class SecurityHomePage(LoginRequiredMixin,UserPassesTestMixin,View):
    template_name = 'security/security_home.html'
    def test_func(self):
        try:
            sec = self.request.user.security
        except:
            raise PermissionDenied
        else:
            security = get_object_or_404(Security, pk=self.kwargs['pk'])
            return security.user.pk == self.request.user.pk
    def get(self, request, pk):
        return render(request,self.template_name)
    def post(self, request, pk):
        try:
            otp = OTP.objects.get(otp=request.POST.get('otp'))
        except:
            return render(request, self.template_name, {'nothing':True})
        else:
            return render(request, self.template_name, {'outpass':otp.outpass})


class InTimeView(LoginRequiredMixin,UserPassesTestMixin,View):
    template_name = "security/intime.html"
    def test_func(self):
        try:
            sec = self.request.user.security
        except:
            raise PermissionDenied
        else:
            security = get_object_or_404(Security, pk=self.kwargs['pk'])
            return security.user.pk == self.request.user.pk
    def get(self, request, pk):
        return render(request, self.template_name)
    def post(self, request, pk):
        try:
            print(request.POST.get('record'))
            outpass = OPRalias.objects.get(alias_no=request.POST.get('record')).outpass
        except:
            return render(request, self.template_name, {'nothing':True})
        else:
            return render(request, self.template_name, {'outpass':outpass,'alias':request.POST.get('record')})



@require_POST
@csrf_exempt
def op_accept(request):
    try:
        sec = request.user.security
    except:
        raise PermissionDenied
    else:
        outpass = get_object_or_404(Outpass, pk=json.loads(request.body).get('pk'))
        if not outpass.tutor_status == 'accepted' and outpass.warden_status == 'accepted' and outpass.expired:
            raise PermissionDenied
        record = OPRecord()
        record.student = outpass.student
        record.accepted_warden =  outpass.accepted_warden
        record.accepted_tutor = outpass.accepted_tutor
        record.req_date = outpass.req_date
        record.reason = outpass.reason
        record.req_days = outpass.req_days
        record.emergency = outpass.emergency
        record.accepted_security = request.user.security
        record.save()
        for tutor in outpass.tutors.all():
            record.tutors.add(tutor)
        for warden in outpass.wardens.all():
            record.wardens.add(warden)
        record.save()
        outpass.security_status = 'accepted'
        outpass.accepted_security = request.user.security
        outpass.expired = True
        outpass.save()
        outpass.otp_set.first().delete()
        opra = OPRalias(
            alias_no = get_record_no(),
            opr = record,
            outpass = outpass
        )
        opra.save()
        return JsonResponse({'accepted':True})


@require_POST
@csrf_exempt
def op_reject(request):
    try:
        sec = request.user.security
    except:
        raise PermissionDenied
    else:
        outpass = get_object_or_404(Outpass, pk=json.loads(request.body).get('pk'))
        if not outpass.tutor_status == 'accepted' and outpass.warden_status == 'accepted' and not outpass.expired:
            raise PermissionDenied
        outpass.security_status = 'rejected'
        outpass.accepted_security = request.user.security
        outpass.expired = True
        outpass.otp_set.first().delete()
        outpass.save()
        return JsonResponse({'rejected':True})

@require_POST
@csrf_exempt
def record_intime(request):
    try:
        sec = request.user.security
    except:
        raise PermissionDenied
    else:
        try:
            record = OPRalias.objects.get(alias_no=json.loads(request.body)['alias'])
        except:
            raise SuspiciousOperation
        else:
            tz = pytz.timezone('Asia/Kolkata')
            date = tz.localize(dt=datetime.datetime.now())
            record.opr.in_time = date
            record.opr.save()
            record.outpass.delete()
            record.delete()
            return HttpResponse()