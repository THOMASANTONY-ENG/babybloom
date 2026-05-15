from django.conf import settings
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response

from django.contrib.auth.models import User
from doctors.models import Doctor
from parents.models import Baby
from appointments.models import Appointment
from prescriptions.models import Prescription
from vaccinations.models import BabyVaccine, VaccineSchedule


from django.utils import timezone
from datetime import timedelta
from parents.models import GrowthLog

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def admin_dashboard_api(request):
    user = request.user
    
    # Auto-create profile if missing (safety for superusers)
    if not hasattr(user, 'profile'):
        from .models import Profile
        role = 'admin' if user.is_superuser else 'parent'
        Profile.objects.create(user=user, role=role)
    
    # Permission check: must be admin role OR superuser
    if not (user.is_superuser or user.profile.role == 'admin'):
        return Response({"error": "Not authorized"}, status=403)

    # Core Stats
    total_users = User.objects.count()
    total_parents = User.objects.filter(profile__role='parent').count()
    total_doctors = Doctor.objects.count()
    total_babies = Baby.objects.count()
    total_appointments = Appointment.objects.count()
    
    # Advanced Stats
    this_month_start = timezone.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    appts_this_month = Appointment.objects.filter(date__gte=this_month_start).count()
    
    # Vaccination stats
    total_vaccines_assigned = BabyVaccine.objects.count()
    vaccines_completed = BabyVaccine.objects.filter(completed=True).count()
    completion_rate = round((vaccines_completed / total_vaccines_assigned * 100), 1) if total_vaccines_assigned > 0 else 0
    
    # Overdue vaccines (Simplified: any pending vaccine past its relative due date)
    # This requires more complex logic if calculated on the fly, 
    # but for dashboard we'll count records explicitly marked or where due_date < today
    # Since we don't have a due_date field in BabyVaccine (it's calculated), 
    # we'll approximate based on completed=False for now or use a more precise query.
    overdue_count = 0
    today = timezone.now().date()
    all_vax = BabyVaccine.objects.filter(completed=False).select_related('baby', 'vaccine')
    for v in all_vax:
        if v.baby.dob + timedelta(days=v.vaccine.due_days) < today:
            overdue_count += 1

    # Growth records
    growth_count = GrowthLog.objects.count()

    # Recent Activity
    recent_appointments = Appointment.objects.select_related('baby').order_by('-date')[:5]
    recent_babies = Baby.objects.order_by('-id')[:5]
    recent_users = User.objects.order_by('-id')[:5]

    return Response({
        "stats": {
            "total_users": total_users,
            "parents": total_parents,
            "doctors": total_doctors,
            "babies": total_babies,
            "total_appointments": total_appointments,
            "appts_this_month": appts_this_month,
            "completion_rate": completion_rate,
            "overdue_vaccines": overdue_count,
            "growth_records": growth_count
        },
        "recent": {
            "appointments": [{
                "id": a.id,
                "baby_name": a.baby.name,
                "date": a.date,
                "status": a.status
            } for a in recent_appointments],
            "babies": [{
                "id": b.id,
                "name": b.name,
                "dob": b.dob
            } for b in recent_babies],
            "users": [{
                "id": u.id,
                "username": u.username,
                "role": getattr(u, 'profile', None) and u.profile.role or ('admin' if u.is_superuser else 'unknown')
            } for u in recent_users],
        }
    })

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def admin_patients_api(request):
    user = request.user
    if not hasattr(user, 'profile'):
        from .models import Profile
        role = 'admin' if user.is_superuser else 'parent'
        Profile.objects.create(user=user, role=role)

    if not (user.is_superuser or user.profile.role == 'admin'):
        return Response({"error": "Not authorized"}, status=403)
    
    babies = Baby.objects.select_related('parent').all().order_by('-id')
    data = [{
        "id": b.id,
        "name": b.name,
        "dob": b.dob,
        "gender": b.gender,
        "parent_name": b.parent.username,
        "parent_email": b.parent.email,
        "weight": b.weight,
        "height": b.height
    } for b in babies]
    return Response(data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_profile(request):
    user = request.user
    
    from .models import Profile
    
    # Ensure profile exists
    if not hasattr(user, 'profile'):
        Profile.objects.create(user=user, role='admin' if user.is_superuser else 'parent')
    
    # Auto-assign admin role to superusers
    if user.is_superuser and user.profile.role != 'admin':
        user.profile.role = 'admin'
        user.profile.save()
        
    return Response({
        "username": user.username,
        "role": user.profile.role,
    })
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def public_doctors_api(request):
    doctors = Doctor.objects.select_related('user').filter(user__is_active=True).order_by('id')
    data = [{
        "id": doc.id,
        "user_id": doc.user.id,
        "username": doc.user.username,
        "speciality": doc.speciality,
        "experience": doc.experience,
    } for doc in doctors]
    return Response(data)

@api_view(['POST'])
def register_api(request):
    data = request.data
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    role = 'parent' # Force public registrations to be parents

    try:
        if not username or not email or not password:
            return Response({"error": "All fields are required"}, status=400)

        if User.objects.filter(username=username).exists():
            return Response({"error": "Username is already taken"}, status=400)
            
        if User.objects.filter(email=email).exists():
            return Response({"error": "An account with this email already exists"}, status=400)

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        from .models import Profile
        # Use update_or_create to prevent "UNIQUE constraint" crashes if signals exist
        Profile.objects.update_or_create(user=user, defaults={'role': role})

        # Send Welcome Email (Non-blocking safety)
        try:
            from notifications.utils import send_welcome_email
            send_welcome_email(user)
        except Exception as e:
            print(f"Non-critical: Welcome email failed: {e}")

        return Response({"message": "User registered successfully"}, status=201)

    except Exception as e:
        import traceback
        print("--- CRITICAL REGISTRATION FAILURE ---")
        traceback.print_exc()
        return Response({"error": f"Server Error: {str(e)}"}, status=500)


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def manage_doctors_api(request):
    user = request.user
    if not hasattr(user, 'profile'):
        from .models import Profile
        role = 'admin' if user.is_superuser else 'parent'
        Profile.objects.create(user=user, role=role)

    if not (user.is_superuser or user.profile.role == 'admin'):
        return Response({"error": "Not authorized"}, status=403)

    if request.method == 'GET':
        doctors = Doctor.objects.select_related('user').all().order_by('-id')
        data = []
        for doc in doctors:
            image_url = ""
            if doc.image:
                image_url = request.build_absolute_uri(doc.image.url)
            
            data.append({
                "id": doc.id,
                "user_id": doc.user.id,
                "username": doc.user.username,
                "email": doc.user.email,
                "speciality": doc.speciality,
                "experience": doc.experience,
                "is_active": doc.user.is_active,
                "bio": getattr(doc, 'bio', ''),
                "image": image_url,
            })
        return Response(data)

    elif request.method == 'POST':
        data = request.data
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        speciality = data.get('speciality', 'General')
        experience = data.get('experience', '0 years')
        bio = data.get('bio', '')
        image = request.FILES.get('image') # Handle file upload

        if not username or not password:
            return Response({"error": "Username and password are required"}, status=400)

        if User.objects.filter(username=username).exists():
            return Response({"error": "Username already exists"}, status=400)

        user = User.objects.create_user(username=username, email=email, password=password)
        from .models import Profile
        Profile.objects.update_or_create(user=user, defaults={'role': 'doctor'})

        doc = Doctor.objects.create(
            user=user, 
            speciality=speciality, 
            experience=experience,
            bio=bio,
            image=image
        )

        # Smart Initialization: Auto-generate 9AM-5PM slots for the next 7 days
        try:
            from appointments.models import DoctorAvailability
            from datetime import date, timedelta
            today = date.today()
            for i in range(1, 8):
                day = today + timedelta(days=i)
                DoctorAvailability.objects.get_or_create(
                    doctor=doc,
                    date=day,
                    defaults={
                        "start_time": "09:00:00",
                        "end_time": "17:00:00",
                        "is_available": True
                    }
                )
        except Exception as e:
            print(f"Schedule Auto-Init failed: {e}")

        return Response({"message": "Doctor profile created and schedule initialized successfully", "id": doc.id}, status=201)


@api_view(['DELETE', 'PATCH'])
@permission_classes([IsAuthenticated])
def modify_doctor_api(request, doc_id):
    user_req = request.user
    if not hasattr(user_req, 'profile'):
        from .models import Profile
        role = 'admin' if user_req.is_superuser else 'parent'
        Profile.objects.create(user=user_req, role=role)

    if not (user_req.is_superuser or user_req.profile.role == 'admin'):
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
def parent_dashboard_api(request):
    if request.user.profile.role != 'parent':
        return Response({"error": "Unauthorized"}, status=403)
    
    parent = request.user
    babies = Baby.objects.filter(parent=parent)
    baby_ids = babies.values_list('id', flat=True)
    
    # Stats
    upcoming_appts = Appointment.objects.filter(baby_id__in=baby_ids, date__gte=timezone.now().date()).count()
    
    overdue_vax = 0
    today = timezone.now().date()
    pending_vax = BabyVaccine.objects.filter(baby_id__in=baby_ids, completed=False).select_related('baby', 'vaccine')
    for v in pending_vax:
        if v.baby.dob + timedelta(days=v.vaccine.due_days) < today:
            overdue_vax += 1
            
    # Recent Activity: Logical separation of Upcoming vs Past
    # Only show future or today's appointments in the primary list
    upcoming_appointments = Appointment.objects.filter(
        baby_id__in=baby_ids, 
        date__gte=timezone.now().date()
    ).select_related('baby', 'doctor__user').order_by('date')[:5]
    
    return Response({
        "stats": {
            "babies_count": babies.count(),
            "upcoming_appointments": upcoming_appts,
            "overdue_vaccines": overdue_vax,
            "total_growth_logs": GrowthLog.objects.filter(baby_id__in=baby_ids).count()
        },
        "recent_appointments": [{
            "id": a.id,
            "baby_name": a.baby.name,
            "doctor_name": a.doctor.user.username if a.doctor else "Unassigned",
            "date": a.date,
            "status": a.status
        } for a in upcoming_appointments],
        "my_babies": [{
            "id": b.id,
            "name": b.name,
            "age": b.age, 
            "gender": b.gender
        } for b in babies]
    })

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_account_api(request):
    """Irreversibly deletes the user account and all associated data."""
    user = request.user
    
    # Safety Lock: Admins cannot delete themselves via this API
    try:
        from .models import Profile
        profile = Profile.objects.get(user=user)
        if profile.role == 'admin':
            return Response({"error": "Administrator accounts cannot be deleted through this interface for safety reasons."}, status=403)
    except:
        pass

    try:
        user.delete()
        return Response({"message": "Account deleted successfully"}, status=204)
    except Exception as e:
        return Response({"error": f"Failed to delete account: {str(e)}"}, status=500)
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

@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def update_profile_api(request):
    """Updates user email and profile phone number."""
    user = request.user
    data = request.data
    
    email = data.get('email')
    phone = data.get('phone_number')
    
    try:
        if email:
            user.email = email
            user.save()
            
        from .models import Profile
        profile, created = Profile.objects.get_or_create(user=user)
        if phone is not None:
            profile.phone_number = phone
            profile.save()
            
        return Response({
            "message": "Profile updated successfully",
            "user": {
                "email": user.email,
                "phone_number": profile.phone_number
            }
        })
    except Exception as e:
        return Response({"error": str(e)}, status=400)

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
