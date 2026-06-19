from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from User.models import UserPrediction


def adminhome(request):
    users = User.objects.all().order_by('-date_joined')
    return render(request, "Admin/adminhome.html", {"users": users})


def admin_update_userstatus(request, user_id):
    user = User.objects.get(id=user_id)
    user.is_active = not user.is_active
    user.save()
    return redirect('adminhome')


def adminuserpredictions(request):
    predictions = UserPrediction.objects.all().select_related('user').order_by('-timestamp')
    return render(request, "Admin/adminuserpredictions.html", {"predictions": predictions})
