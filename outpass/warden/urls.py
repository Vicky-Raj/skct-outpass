from django.urls import path
from . import views

urlpatterns = [
    path('login/',views.WardenLoginView.as_view(),name='warden-login'),
    path('<int:pk>/home/',views.WardenHomePage.as_view(),name='warden-home'),
    path('<int:pk>/emergency/outpass/',views.EmergencyOutpassView.as_view(),name='emergency'),
    path('<int:pk>/holiday/outpass/',views.HolidayOutpassView.as_view(),name='holiday'),
    path('students/',views.WardenStudentsView.as_view(),name='warden-students-view'),
    path('outpass/accept/',views.op_accept),
    path('outpass/reject/',views.op_reject),
    path('log/',views.WardenLogView.as_view(),name='warden-log')
]