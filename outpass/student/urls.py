from django.urls import path
from . import views

urlpatterns = [
    path('login/',views.StudentLoginView.as_view(),name='student-login'),
    path('<int:pk>/home/',views.StudentHomePage.as_view(),name='student-home'),
    path('<int:pk>/outpass/create/',views.OutpassCreateView.as_view(), name='op-form'),
    path('outpass/delete/',views.op_delete,name='op-delete'),
    path('otp/gen/',views.gen_otp,name='otp-gen'),
    path('<int:pk>/profile/',views.ProfileView.as_view(),name='student-profile')
]