from django.utils.decorators import method_decorator
from django.shortcuts import render,redirect
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login, logout
from django.contrib.auth.decorators import login_required

from .models import Profile
from doctors.models import Doctor
from appointments.models import Appointment
from parents.models import Baby
from prescriptions.models import Prescription
from rest_framework.decorators import api_view
from rest_framework.response import Response


@api_view(['GET'])
def test_api(request):
    return Response({"message": "API working"})

def register(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        role = request.POST['role']

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        user.profile.role = role
        user.profile.save()

        if role == 'doctor':
            Doctor.objects.create(user=user)

        return redirect('login')

    return render(request, 'accounts/register.html')

def login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request, username=username, password=password)

        if user is not None:
            auth_login(request, user)

            # Auto-assign admin role to superusers
            if user.is_superuser and (not hasattr(user, 'profile') or user.profile.role != 'admin'):
                profile, created = Profile.objects.get_or_create(user=user)
                profile.role = 'admin'
                profile.save()

            if user.profile.role == 'parent':
                return redirect('parent_dashboard')
            elif user.profile.role == 'doctor':
                return redirect('doctor_dashboard')
            elif user.profile.role == 'admin':
                return redirect('admin_dashboard')

        else:
            messages.error(request, "Invalid credentials")

    return render(request, 'accounts/login.html')
def admin_required(view_func):
    def wrapper(request, *args, **kwargs):
        if request.user.profile.role != 'admin':
            return redirect('login')
        return view_func(request, *args, **kwargs)
    return wrapper
@login_required
@admin_required
def admin_dashboard(request):
    users = User.objects.count()
    doctors = Doctor.objects.count()
    appointments = Appointment.objects.count()
    babies = Baby.objects.count()

    from vaccinations.models import Vaccine
    vaccines = Vaccine.objects.count()



    recent_appointments = Appointment.objects.order_by('-date')[:5]
    recent_prescriptions = Prescription.objects.order_by('-id')[:5]
    recent_users = User.objects.order_by('-id')[:5]

    context = {
        'users': users,
        'doctors': doctors,
        'appointments': appointments,
        'babies': babies,
        'vaccines': vaccines,

        'recent_appointments': recent_appointments,
        'recent_prescriptions': recent_prescriptions,
        'recent_users': recent_users,
    }

    return render(request, 'accounts/admin_dashboard.html', context)
def home_view(request):
    if request.user.is_authenticated:
        if hasattr(request.user, 'profile'):
            if request.user.profile.role == 'parent':
                return redirect('parent_dashboard')
            elif request.user.profile.role == 'doctor':
                return redirect('doctor_dashboard')
            elif request.user.profile.role == 'admin':
                return redirect('admin_dashboard')
        elif request.user.is_superuser:
            return redirect('admin_dashboard')
    return render(request,'accounts/home.html')    

@login_required
def parent_dashboard(request):
    if request.user.profile.role != "parent":
        return redirect("unauthorized")  
    return render(request, 'accounts/parent_dashboard.html')
    
@login_required
def doctor_dashboard(request):
    if request.user.profile.role != "doctor":
        return redirect("unauthorized")  
    return render(request, 'accounts/doctor_dashboard.html')

def unauthorized(request):
    return render(request, 'accounts/unauthorized.html')

def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
@admin_required
def user_list(request):
    users = User.objects.all()
    return render(request,"accounts/user_list.html",{'users':users})

@login_required
@admin_required
def delete_user(request, user_id):
    user = User.objects.get(id=user_id)
    if user == request.user:
        return redirect('user_list')
    user.delete()
    return redirect('user_list')
