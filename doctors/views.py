from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Doctor
from django.contrib.auth.models import User
from accounts.views import admin_required

# Create your views here.
@login_required
@admin_required
def doctor_list(request):
    doctors = Doctor.objects.all()
    return render(request, 'doctors/doctor_list.html', {'doctors': doctors})

@login_required
@admin_required
def add_doctor(request):
    if request.method == "POST":

        username = request.POST['username']
        password = request.POST['password']
        speciality = request.POST['speciality']
        experience = request.POST['experience']

        user = User.objects.create_user(
            username = username,
            password = password
        )

        user.profile.role = "doctor"
        user.profile.save()
        Doctor.objects.create(
            user = user,
            speciality = speciality,
            experience = experience
        )
        return redirect("doctor_list")

    else:
        return render(request, 'doctors/add_doctor.html')

@login_required
@admin_required
def delete_doctor(request, doctor_id):
    doctor = get_object_or_404(Doctor, id=doctor_id)

    if doctor.appointment_set.exists():
        return redirect('doctor_list')

    doctor.user.delete()

    return redirect('doctor_list')