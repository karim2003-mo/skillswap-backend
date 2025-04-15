from django.urls import path
from .views import *
urlpatterns = [
    path('hellouser/',hellouser,name='hellouser'),
]
