from django.shortcuts import render,redirect
from django.views import View
from django.contrib.auth import authenticate
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import logout

class HomeView(View):
    def get(self, request):
        if 'role' in request.COOKIES:
            role = request.COOKIES.get('role')
            if role == 'student' and request.user.is_authenticated:
                try:
                    return redirect('student-home', pk=request.user.student.pk)
                except:
                    return redirect('home-view')
            elif role == 'tutor' and request.user.is_authenticated:
                try:
                    return redirect('tutor-home', pk=request.user.tutor.pk)
                except:
                    return redirect('home-view')
            elif role == 'warden' and request.user.is_authenticated:
                try:
                    return redirect('warden-home', pk=request.user.warden.pk)
                except:
                    return redirect('home-view')
            elif role == 'security' and request.user.is_authenticated:
                try:
                    return redirect('sec-home', pk=request.user.security.pk)
                except:
                    return redirect('home-view')
        
        return render(request, 'home/index.html')

class ResetPassword(LoginRequiredMixin,View):
    template_name='home/reset.html'
    def get(self, request):
        return render(request,self.template_name)
    def post(self, request):
        request.user.set_password(request.POST.get('password'))
        request.user.save()
        return redirect('logout')


class LogoutView(View):
    def get(self, request):
        logout(request)
        response = redirect('home-view')
        response.delete_cookie('role')
        return response