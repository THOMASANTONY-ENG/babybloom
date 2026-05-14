from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from django.contrib.auth.models import User
from doctors.models import Doctor
from parents.models import Baby
from appointments.models import Appointment
from prescriptions.models import Prescription
from vaccinations.models import Vaccine


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def admin_dashboard_api(request):

  
    if request.user.profile.role != 'admin':
        return Response({"error": "Not authorized"})

  
    users = User.objects.count()
    doctors = Doctor.objects.count()
    babies = Baby.objects.count()
    appointments = Appointment.objects.count()
    vaccines = Vaccine.objects.count()

    recent_appointments = Appointment.objects.order_by('-date')[:5].values(
        'id', 'date', 'status'
    )

    recent_prescriptions = Prescription.objects.order_by('-id')[:5].values(
        'id', 'medication'
    )

    recent_users = User.objects.order_by('-id')[:5].values(
        'id', 'username'
    )

    return Response({
        "stats": {
            "users": users,
            "doctors": doctors,
            "babies": babies,
            "appointments": appointments,
            "vaccines": vaccines,
        },
        "recent": {
            "appointments": list(recent_appointments),
            "prescriptions": list(recent_prescriptions),
            "users": list(recent_users),
        }
    })
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_profile(request):
    user = request.user
    
    # Auto-assign admin role to superusers
    if user.is_superuser and user.profile.role != 'admin':
        user.profile.role = 'admin'
        user.profile.save()
        
    return Response({
        "username": user.username,
        "role": user.profile.role,
    })
@api_view(['POST'])
def register_api(request):
    data = request.data
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    role = 'parent' # Force public registrations to be parents

    if User.objects.filter(username=username).exists():
        return Response({"error": "Username already exists"}, status=400)

    user = User.objects.create_user(
        username=username,
        email=email,
        password=password
    )

    user.profile.role = role
    user.profile.save()

    return Response({"message": "User registered successfully"})


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def manage_doctors_api(request):
    if request.user.profile.role != 'admin':
        return Response({"error": "Not authorized"}, status=403)

    if request.method == 'GET':
        doctors = Doctor.objects.select_related('user').all().order_by('-id')
        data = [{
            "id": doc.id,
            "user_id": doc.user.id,
            "username": doc.user.username,
            "email": doc.user.email,
            "speciality": doc.speciality,
            "experience": doc.experience,
            "is_active": doc.user.is_active,
        } for doc in doctors]
        return Response(data)

    elif request.method == 'POST':
        username = request.data.get('username')
        email = request.data.get('email')
        password = request.data.get('password')
        speciality = request.data.get('speciality', 'General')
        experience = request.data.get('experience', '0 years')

        if not username or not password:
            return Response({"error": "Username and password are required"}, status=400)

        if User.objects.filter(username=username).exists():
            return Response({"error": "Username already exists"}, status=400)

        user = User.objects.create_user(username=username, email=email, password=password)
        user.profile.role = 'doctor'
        user.profile.save()

        doc = Doctor.objects.create(user=user, speciality=speciality, experience=experience)
        return Response({"message": "Doctor created successfully", "id": doc.id})


@api_view(['DELETE', 'PATCH'])
@permission_classes([IsAuthenticated])
def modify_doctor_api(request, doc_id):
    if request.user.profile.role != 'admin':
        return Response({"error": "Not authorized"}, status=403)

    try:
        doctor = Doctor.objects.get(id=doc_id)
    except Doctor.DoesNotExist:
        return Response({"error": "Doctor not found"}, status=404)

    if request.method == 'DELETE':
        user = doctor.user
        user.delete() # Deletes user and cascaded doctor profile
        return Response({"message": "Doctor deleted successfully"})

    elif request.method == 'PATCH':
        user = doctor.user
        
        # If specific fields are provided, update them
        if 'speciality' in request.data:
            doctor.speciality = request.data.get('speciality')
        if 'experience' in request.data:
            doctor.experience = request.data.get('experience')
        if 'email' in request.data:
            user.email = request.data.get('email')
            user.save()
            
        doctor.save()
        
        # If no specific fields, toggle active status (backward compatibility)
        if not any(k in request.data for k in ['speciality', 'experience', 'email']):
            user.is_active = not user.is_active
            user.save()
            status_text = "enabled" if user.is_active else "disabled"
            return Response({"message": f"Doctor {status_text} successfully", "is_active": user.is_active})
            
        return Response({"message": "Doctor updated successfully"})

from .models import Notification

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_notifications(request):
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')[:10]
    data = [{
        "id": n.id,
        "message": n.message,
        "is_read": n.is_read,
        "created_at": n.created_at
    } for n in notifications]
    return Response(data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def mark_notification_read(request, notif_id):
    try:
        notification = Notification.objects.get(id=notif_id, user=request.user)
        notification.is_read = True
        notification.save()
        return Response({"message": "Marked as read"})
    except Notification.DoesNotExist:
        return Response({"error": "Notification not found"}, status=404)
