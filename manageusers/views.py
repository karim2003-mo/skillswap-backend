from django.shortcuts import HttpResponse
def hellouser(request):
    return HttpResponse("Hello User!")
# Create your views here.
