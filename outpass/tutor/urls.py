from django.urls import path
from . import views

urlpatterns = [
    path('login/',views.TutorLoginView.as_view(),name='tutor-login'),
    path('<int:pk>/home/',views.TutorHomePage.as_view(),name='tutor-home'),
    path('outpass/accept/',views.op_accept,name='op-accept'),
    path('outpass/reject/',views.op_reject,name='op-reject'),
    path('log/',views.TutorLogView.as_view(),name='tutor-log'),
    path('students/',views.TutorStudentsView.as_view(),name='tutor-students-log'),
]
