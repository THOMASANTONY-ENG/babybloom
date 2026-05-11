from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Appointment
from .serializers import AppointmentSerializer
from .models import Doctor
from accounts.models import Notification
from prescriptions.serializers import PrescriptionSerializer
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