from django.shortcuts import render, redirect
from django.http import HttpResponse
from .plate_capture import start_camera_loop, stop_event
import threading

# Create your views here.

from django.http import HttpResponse
from .plate_capture import start_camera_loop
import threading



def index(request):
    return render(request, "index.html")

def index2(request):
    return render(request, "index2.html")


def start_camera(request):
    if stop_event.is_set():
        stop_event.clear()
    thread = threading.Thread(target=start_camera_loop)
    thread.start()
    return redirect('index2')


def stop_camera(request):
    stop_event.set()
    return redirect('index2')
