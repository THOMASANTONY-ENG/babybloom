from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Prescription
from .serializers import PrescriptionSerializer
from appointments.models import Appointment
from doctors.models import Doctor
from django.shortcuts import get_object_or_404

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_prescription(request):
    appointment_id = request.data.get('appointment_id')
    appointment = get_object_or_404(Appointment, id=appointment_id)
   
    if appointment.status != 'completed':
        return Response({'message': 'Appointment is not completed'}, status=400)

    data = request.data.copy()
    serializer = PrescriptionSerializer(data=data)

    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=201)

    return Response(serializer.errors, status=400)


    
    
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_prescriptions(request):
    Prescriptions = Prescription.objects.filter(
        appointment__baby__parent = request.user
    )

    serializer = PrescriptionSerializer(Prescriptions,many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_doctor_prescriptions(request):
    doctor = get_object_or_404(Doctor, user=request.user)
    prescriptions = Prescription.objects.filter(
        appointment__doctor=doctor
    )

    serializer = PrescriptionSerializer(prescriptions, many=True)
    return Response(serializer.data)