from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Appointment
from .serializers import AppointmentSerializer
from .models import Doctor
from accounts.models import Notification
from prescriptions.models import Prescription
from prescriptions.serializers import PrescriptionSerializer
from parents.serializers import GrowthLogSerializer
from parents.models import GrowthLog, Baby
from django.shortcuts import get_object_or_404
from vaccinations.models import BabyVaccine
from vaccinations.serializers import BabyVaccineSerializer

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def book_appointment(request):
    data = request.data.copy()

    serializer = AppointmentSerializer(data=data)

    if serializer.is_valid():
        appointment = serializer.save()
        # Notify the parent
        Notification.objects.create(
            user=request.user,
            message=f"Your appointment for {appointment.baby.name} on {appointment.date} has been booked and is pending approval."
        )
        return Response(serializer.data)

    return Response(serializer.errors)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_parent_appointments(request):
    appointments = Appointment.objects.filter(baby__parent=request.user)
    serializer = AppointmentSerializer(appointments, many=True)
    return Response(serializer.data)
    

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_doctor_appointments(request):
    doctor = Doctor.objects.get(user=request.user)
    appointments = Appointment.objects.filter(doctor=doctor)

    serializer = AppointmentSerializer(appointments, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_doctor_dashboard(request):
    try:
        doctor = Doctor.objects.get(user=request.user)
    except Doctor.DoesNotExist:
        return Response({"error": "Doctor profile not found"}, status=404)

    appointments = Appointment.objects.filter(doctor=doctor)
    
    stats = {
        "total": appointments.count(),
        "pending": appointments.filter(status='pending').count(),
        "approved": appointments.filter(status='approved').count(),
        "completed": appointments.filter(status='completed').count(),
        "babies": appointments.values('baby').distinct().count(),
    }

    recent_appointments = AppointmentSerializer(
        appointments.order_by('-date')[:5], 
        many=True
    ).data

    return Response({
        "stats": stats,
        "recent_appointments": recent_appointments
    })

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_appointment_status(request, appointment_id):
    appointment = Appointment.objects.get(id=appointment_id)

    status = request.data.get('status')
    appointment.status = status
    appointment.save()

    # Notify the parent
    Notification.objects.create(
        user=appointment.baby.parent,
        message=f"Appointment for {appointment.baby.name} on {appointment.date} has been {status}."
    )

    return Response({"message": "Updated"})
from prescriptions.models import Prescription

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_prescription(request):
    appointment_id = request.data.get('appointment')
    appointment = Appointment.objects.get(id=appointment_id)
    
    # Check if the user is the doctor for this appointment
    try:
        doctor = Doctor.objects.get(user=request.user)
        if appointment.doctor != doctor:
            return Response({"error": "You are not authorized to prescribe for this appointment"}, status=403)
    except Doctor.DoesNotExist:
        return Response({"error": "Only doctors can create prescriptions"}, status=403)

    # Check if prescription already exists
    existing_prescription = Prescription.objects.filter(appointment=appointment).first()
    
    if existing_prescription:
        serializer = PrescriptionSerializer(existing_prescription, data=request.data)
    else:
        serializer = PrescriptionSerializer(data=request.data)

    if serializer.is_valid():
        prescription = serializer.save()
        # Notify the parent
        Notification.objects.create(
            user=prescription.appointment.baby.parent,
            message=f"A prescription has been {'updated' if existing_prescription else 'added'} for {prescription.appointment.baby.name}."
        )
        return Response(serializer.data)

    return Response(serializer.errors, status=400)
@api_view(['GET'])
@permission_classes([IsAuthenticated])

def patient_history(request, baby_id):
    baby = get_object_or_404(Baby, id=baby_id)
    
    # Check permissions: Only Parent, Assigned Doctor, or Admin can see history
    is_parent = baby.parent == request.user
    is_admin = request.user.is_staff
    is_doctor = False
    
    if hasattr(request.user, 'doctor'):
        is_doctor = Appointment.objects.filter(baby=baby, doctor=request.user.doctor).exists()
    
    if not (is_parent or is_doctor or is_admin):
        return Response({"message": "You are not authorized to view this history"}, status=403)

    appointments = Appointment.objects.filter(
        baby_id=baby_id
    )

    prescriptions = Prescription.objects.filter(
        appointment__baby_id=baby_id
    )

    growth_records = GrowthLog.objects.filter(
        baby_id=baby_id
    )

    vaccines = BabyVaccine.objects.filter(
        baby_id=baby_id
    )

    return Response({

        "appointments":
            AppointmentSerializer(
                appointments,
                many=True
            ).data,

        "prescriptions":
            PrescriptionSerializer(
                prescriptions,
                many=True
            ).data,

        "growth":
            GrowthLogSerializer(
                growth_records,
                many=True
            ).data,

        "vaccines":
            BabyVaccineSerializer(
                vaccines,
                many=True
            ).data
    })