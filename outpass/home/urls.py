from django.urls import path
from .views import HomeView,LogoutView,ResetPassword

urlpatterns = [
    path('',HomeView.as_view(),name='home-view'),
    path('logout/',LogoutView.as_view(),name='logout'),
    path('reset/',ResetPassword.as_view(),name='reset')

]