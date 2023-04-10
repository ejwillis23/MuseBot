from django.urls import path

from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('sign-in', views.sign_in, name='sign-in'),
    path('after-sign-in', views.after_sign_in, name='after-sign-in'),
]
