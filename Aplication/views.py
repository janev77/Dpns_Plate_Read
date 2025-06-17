from django.shortcuts import render

# Create your views here.

from django.http import HttpResponse
from .plate_capture import start_camera_loop
import threading

def start_camera(request):
    thread = threading.Thread(target=start_camera_loop)
    thread.start()
    return HttpResponse("Камерата е стартувана. Затвори прозорецот со 'q'.")
