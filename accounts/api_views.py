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
    return Response({
        "username": request.user.username,
        "role": request.user.profile.role,
    })
