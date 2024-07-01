from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def home(request):
    context = {"active": "home"}
    return render(request, "home.html", context)


def handler500(request):
    """To show our 500.html template instead of django default one"""
    return render(request, "500.html", status=500)
