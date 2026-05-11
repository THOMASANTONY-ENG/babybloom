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
    
    doctor = get_object_or_404(Doctor, user=request.user)
    if appointment.doctor != doctor:
        return Response({'message': 'You are not authorized to add prescription for this appointment'}, status=403)
   
    if appointment.status != 'completed':
        return Response({'message': 'Appointment is not completed'}, status=400)

    if hasattr(appointment, 'prescription'):
        return Response({'message': 'Prescription already exists for this appointment'}, status=400)

    data = request.data.copy()
    data['appointment'] = appointment_id
    serializer = PrescriptionSerializer(data=data)

    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=201)

    return Response(serializer.errors, status=400)


    
    
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_prescriptions(request):
    prescriptions = Prescription.objects.filter(
        appointment__baby__parent = request.user
    )

    serializer = PrescriptionSerializer(prescriptions,many=True)
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

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_prescription_by_appointment(request, appointment_id):
    prescription = Prescription.objects.filter(appointment_id=appointment_id).first()
    if not prescription:
        return Response({"error": "Prescription not found"}, status=404)
    
    serializer = PrescriptionSerializer(prescription)
    return Response(serializer.data)

@api_view(['PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
def edit_prescription(request, pk):
    prescription = get_object_or_404(Prescription, pk=pk)
    
    doctor = get_object_or_404(Doctor, user=request.user)
    if prescription.appointment.doctor != doctor:
        return Response({'message': 'You are not authorized to edit this prescription'}, status=403)

    serializer = PrescriptionSerializer(prescription, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    
    return Response(serializer.errors, status=400)