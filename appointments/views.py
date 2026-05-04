from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from functools import wraps
from parents.models import Baby
from doctors.models import Doctor
from .models import Appointment

# Decorator to restrict views to doctors only
def doctor_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not hasattr(request.user, 'profile') or request.user.profile.role != "doctor":
            return redirect("home")
        return view_func(request, *args, **kwargs)
    return wrapper

# Create your views here.
@login_required
def book_appointment(request):
    babies = Baby.objects.filter(parent=request.user)
    doctors = Doctor.objects.all()
    if request.method == "POST":
        baby_id = request.POST["baby"]
        doctor_id = request.POST["doctor"]
        date = request.POST["date"]
        time = request.POST["time"]

        Appointment.objects.create(
            baby_id=baby_id,
            doctor_id=doctor_id,
            date=date,
            time=time,
            status="scheduled",
        )
        return redirect("view_appointments")

    return render(
        request, "appointments/book.html", {"babies": babies, "doctors": doctors}
    )

@login_required
def view_appointments(request):
    appointments = Appointment.objects.filter(baby__parent=request.user)
    return render(request, "appointments/list.html", {"appointments": appointments})

@login_required
@doctor_required
def doctor_appointments(request):
    try:
        doctor = Doctor.objects.get(user=request.user)
        appointments = Appointment.objects.filter(doctor=doctor)
    except Doctor.DoesNotExist:
        appointments = []
        
    return render(request, "appointments/doctor_list.html", {"appointments": appointments})

@login_required
@doctor_required
def update_appointment(request, appointment_id):
    doctor = get_object_or_404(Doctor, user=request.user)
    appointment = get_object_or_404(Appointment, id=appointment_id, doctor=doctor)
    
    if request.method == "POST":
        status = request.POST["status"]
        appointment.status = status
        appointment.save()
        return redirect("doctor_appointments")
    
    return render(request, "appointments/update.html", {"appointment": appointment})
