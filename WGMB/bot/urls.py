from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('register', views.register, name='register'),
    path('user', views.user, name='user'),
    path('history', views.histroy, name='history'),
    path('day', views.day, name='day')
]
