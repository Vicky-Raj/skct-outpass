from django.urls import path
from . import views


urlpatterns = [
    path('login/',views.SecurityLoginView.as_view(),name='security-login'),
    path('<int:pk>/home/',views.SecurityHomePage.as_view(),name='sec-home'),
    path('<int:pk>/intime/',views.InTimeView.as_view(),name='intime'),
    path('record/intime/',views.record_intime,name='intime-record'),
    path('op/accept/',views.op_accept,name='op-accept'),
    path('op/reject/',views.op_reject,name='op-reject'),

]