from django.shortcuts import render,get_object_or_404,redirect
from django.views import View
from .models import Tutor
import json
from api.views import request_notification,status_notification
import threading
from student.models import Student
from django.http import JsonResponse
from home.models import Outpass
from django.core.exceptions import PermissionDenied
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.contrib.auth.models import User
from django.contrib.auth import authenticate,login
from django.contrib.auth.mixins import UserPassesTestMixin,LoginRequiredMixin
from home.models import OPRecord
from django.conf import settings

class TutorLoginView(View):
    template_name = 'home/login.html'
    def get(self, request):
        return render(request, self.template_name,{'tutor':True})
    def post(self, request):
        try:
            user = Tutor.objects.get(
                user=User.objects.get(email=request.POST.get('email'))
                ).user
        except:
            return render(request, self.template_name,
            {'tutor':True,
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
                {'tutor':True,
                'wrong':True,
                'email':request.POST.get('email'),
                })
            login(request,user)
            response =  redirect('tutor-home', pk=Tutor.objects.get(user=user).pk)
            response.set_cookie('role', 'tutor',max_age=60*60*24*365)
            return response

class TutorHomePage(UserPassesTestMixin,View):
    template_name = 'tutor/tutor_home.html'
    def test_func(self):
        try:
            tut = self.request.user.tutor
        except:
            return PermissionDenied
        else:
            tutor = get_object_or_404(Tutor, pk=self.kwargs['pk'])
            return tutor.user.pk == self.request.user.pk
    def get(self, request,pk):
        outpasses = [outpass for outpass in request.user.tutor.tutor_outpass.all().order_by('dep_date') if outpass.tutor_status == 'pending']
        return render(request, self.template_name,{'outpasses':outpasses})



class TutorLogView(LoginRequiredMixin,View):
    template_name="tutor/log.html"
    def get(self,request):
        try:
            tu = request.user.tutor
        except:
            raise PermissionDenied
        else:
            if request.GET.get('date') == None:
                return render(request,self.template_name,{'records':request.user.tutor.tutor_log.all().order_by('-dep_date')})
            else:
                date = request.GET.get('date').split('/')
                records = OPRecord.objects.filter(dep_date__year=date[2],dep_date__month=date[0],dep_date__day=date[1],tutors__in=[request.user.tutor])
                return render(request,self.template_name,{'records':records})

class TutorStudentsView(LoginRequiredMixin, View):
    template_name = 'tutor/student_log.html'
    def get(self, request):
        year = 1
        if not request.GET.get('rollno') == '' and request.GET.get('rollno'):
            students = Student.objects.filter(reg_no__istartswith=request.GET.get('rollno'),tutors__in=[request.user.tutor]).order_by('pk')
            return render(request, self.template_name, {'students':students,'value':request.GET.get('rollno')})
        if request.GET.get('year'):
            year = request.GET.get('year')
        students = [student for student in request.user.tutor.student_set.all().order_by('pk') 
            if ((int(settings.YEAR) - int(student.batch.split('-')[0]))+1) == int(year)]
        return render(request, self.template_name, {'students':students})
                

@require_POST
@csrf_exempt
def op_accept(request):
    try:
        tu = request.user.tutor
    except:
        raise PermissionDenied
    else:
        outpass = get_object_or_404(Outpass, pk=json.loads(request.body).get('pk'))
        if not request.user.tutor in outpass.tutors.all():
            raise PermissionDenied
        elif not outpass.tutor_status == 'pending':
            raise PermissionDenied
        else:
            outpass.accepted_tutor = request.user.tutor
            outpass.tutor_status = 'accepted'
            outpass.save()
            th1 = threading.Thread(target=request_notification,args=(outpass.student,'warden'))
            th2 = threading.Thread(target=status_notification,args=(outpass.student,'accepted','tutor'))
            th1.start()
            th2.start()
            return JsonResponse({'accepted':True})

@require_POST
@csrf_exempt
def op_reject(request):
    try:
        tu = request.user.tutor
    except:
        raise PermissionDenied
    else:
        outpass = get_object_or_404(Outpass, pk=json.loads(request.body).get('pk'))
        if not request.user.tutor in outpass.tutors.all():
            raise PermissionDenied
        if not outpass.tutor_status == 'pending':
            raise PermissionDenied
        else:
            outpass.accepted_tutor = request.user.tutor
            outpass.tutor_status = 'rejected'
            outpass.expired = True
            outpass.save()
            th = threading.Thread(target=status_notification,args=(outpass.student,'rejected','tutor'))
            th.start()
            return JsonResponse({'rejected':True})