from datetime import timedelta, date
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from .models import Appointment, DoctorAvailability, Doctor
from .serializers import AppointmentSerializer, DoctorAvailabilitySerializer
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
    data['parent'] = request.user.id
    
    slot_id = data.get('slot_id')
    slot = None
    if slot_id:
        try:
            slot = DoctorAvailability.objects.get(id=slot_id)
            data['date'] = slot.date
            data['time'] = slot.start_time
            data['doctor'] = slot.doctor.id
        except DoctorAvailability.DoesNotExist:
            return Response({"error": "Selected slot does not exist."}, status=400)
        
        if slot.is_booked:
            return Response({"error": "This slot is already booked."}, status=400)

    serializer = AppointmentSerializer(data=data)
    if serializer.is_valid():
        appointment = serializer.save()
        
        if slot:
            slot.is_booked = True
            slot.save()
            
        # Notify the parent
        Notification.objects.create(
            user=request.user,
            message=f"Your appointment for {appointment.baby.name} on {appointment.date} has been booked and is pending approval."
        )
        return Response(serializer.data)
    return Response(serializer.errors, status=400)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_parent_appointments(request):
    appointments = Appointment.objects.filter(baby__parent=request.user)
    serializer = AppointmentSerializer(appointments, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_doctor_appointments(request):
    try:
        doctor = Doctor.objects.get(user=request.user)
    except Doctor.DoesNotExist:
        return Response({"error": "Doctor profile not found"}, status=404)
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

    all_appointments = Appointment.objects.filter(doctor=doctor)
    
    stats = {
        "total": all_appointments.count(),
        "pending": all_appointments.filter(status='pending').count(),
        "approved": all_appointments.filter(status='approved').count(),
        "completed": all_appointments.filter(status='completed').count(),
        "babies": all_appointments.values('baby').distinct().count(),
    }

    # Logical Archiving: Only show Pending/Approved in the main stream. 
    # Completed appointments are archived to history.
    recent_appointments = AppointmentSerializer(
        all_appointments.filter(status__in=['pending', 'approved']).order_by('date')[:10], 
        many=True
    ).data

    return Response({
        "stats": stats,
        "active_appointments": recent_appointments # Renamed for logical clarity
    })

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_appointment_status(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)
    user = request.user
    
    # Authorization: Only the assigned doctor or an admin can update status
    is_admin = user.is_staff or (hasattr(user, 'profile') and user.profile.role == 'admin')
    is_assigned_doctor = hasattr(user, 'doctor') and appointment.doctor.user == user
    
    if not (is_admin or is_assigned_doctor):
        return Response({"error": "You are not authorized to update this appointment."}, status=403)
        
    status = request.data.get('status')
    if status not in ['pending', 'approved', 'completed', 'cancelled']:
        return Response({"error": "Invalid status."}, status=400)
        
    appointment.status = status
    appointment.save()

    # Notify the parent
    try:
        parent_user = appointment.baby.parent
        Notification.objects.create(
            user=parent_user,
            message=f"Appointment for {appointment.baby.name} on {appointment.date} has been {status}."
        )
    except Exception as e:
        print(f"Notification failed: {e}")

    return Response({"message": f"Appointment successfully {status}"})

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_prescription(request):
    appointment_id = request.data.get('appointment')
    appointment = get_object_or_404(Appointment, id=appointment_id)
    
    try:
        doctor = Doctor.objects.get(user=request.user)
        if appointment.doctor != doctor:
            return Response({"error": "Not authorized"}, status=403)
    except Doctor.DoesNotExist:
        return Response({"error": "Only doctors can prescribe"}, status=403)

    existing = Prescription.objects.filter(appointment=appointment).first()
    serializer = PrescriptionSerializer(existing, data=request.data) if existing else PrescriptionSerializer(data=request.data)

    if serializer.is_valid():
        prescription = serializer.save()
        Notification.objects.create(
            user=prescription.appointment.baby.parent,
            message=f"Prescription updated for {prescription.appointment.baby.name}."
        )
        return Response(serializer.data)
    return Response(serializer.errors, status=400)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def patient_history(request, baby_id):
    baby = get_object_or_404(Baby, id=baby_id)
    
    # Simple permission check
    if not (baby.parent == request.user or request.user.is_staff or hasattr(request.user, 'doctor')):
        return Response({"message": "Unauthorized"}, status=403)

    appointments = Appointment.objects.filter(baby=baby)
    prescriptions = Prescription.objects.filter(appointment__baby=baby)
    growth = GrowthLog.objects.filter(baby=baby)
    vaccines = BabyVaccine.objects.filter(baby=baby)

    return Response({
        "appointments": AppointmentSerializer(appointments, many=True).data,
        "prescriptions": PrescriptionSerializer(prescriptions, many=True).data,
        "growth": GrowthLogSerializer(growth, many=True).data,
        "vaccines": BabyVaccineSerializer(vaccines, many=True).data
    })

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_availability(request):
    try:
        doctor = Doctor.objects.get(user=request.user)
    except Doctor.DoesNotExist:
        return Response({"error": "Only doctors can create availability"}, status=403)
        
    data = request.data.copy()
    data['doctor'] = doctor.id # Automatically assign to current doctor
    
    serializer = DoctorAvailabilitySerializer(data=data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=201)
    return Response(serializer.errors, status=400)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def available_slots(request, doctor_id):
    date = request.GET.get("date")
    slots = DoctorAvailability.objects.filter(
        doctor_id=doctor_id,
        date=date,
        is_booked=False
    )
    serializer = DoctorAvailabilitySerializer(slots, many=True)
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def bulk_create_availability(request):
    """
    Generate slots for a specific day of the week for the next X weeks.
    Expected: { day_of_week, start_time, end_time, slot_duration, weeks }
    """
    try:
        doctor = Doctor.objects.get(user=request.user)
    except Doctor.DoesNotExist:
        return Response({"error": "Only doctors can manage availability"}, status=403)

    try:
        days_of_week = request.data.get('days_of_week', []) # Expecting list: [0, 1, 2]
        if not days_of_week:
            days_of_week = [int(request.data.get('day_of_week', 0))]
            
        start_time_str = request.data.get('start_time')
        end_time_str = request.data.get('end_time')
        duration = int(request.data.get('slot_duration', 30))
        weeks = int(request.data.get('weeks', 4))
    except (TypeError, ValueError):
        return Response({"error": "Invalid parameters"}, status=400)

    from datetime import datetime, time, timedelta

    try:
        start_t = datetime.strptime(start_time_str, "%H:%M").time()
        end_t = datetime.strptime(end_time_str, "%H:%M").time()
    except ValueError:
        return Response({"error": "Invalid time format. Use HH:MM"}, status=400)
    
    today = date.today()
    created_count = 0

    for i in range(weeks * 7):
        current_date = today + timedelta(days=i)
        if current_date.weekday() in days_of_week:
            curr_dt = datetime.combine(current_date, start_t)
            end_dt = datetime.combine(current_date, end_t)
            
            while curr_dt + timedelta(minutes=duration) <= end_dt:
                slot_start = curr_dt.time()
                slot_end = (curr_dt + timedelta(minutes=duration)).time()
                
                if not DoctorAvailability.objects.filter(
                    doctor=doctor, 
                    date=current_date, 
                    start_time=slot_start
                ).exists():
                    DoctorAvailability.objects.create(
                        doctor=doctor,
                        date=current_date,
                        start_time=slot_start,
                        end_time=slot_end
                    )
                    created_count += 1
                
                curr_dt += timedelta(minutes=duration)

    return Response({"message": f"Successfully created {created_count} slots."})

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_upcoming_slots(request):
    try:
        doctor = Doctor.objects.get(user=request.user)
    except Doctor.DoesNotExist:
        return Response({"error": "Unauthorized"}, status=403)
    
    slots = DoctorAvailability.objects.filter(
        doctor=doctor,
        date__gte=date.today()
    ).order_by('date', 'start_time')
    
    serializer = DoctorAvailabilitySerializer(slots, many=True)
    return Response(serializer.data)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_availability(request, slot_id):
    try:
        doctor = Doctor.objects.get(user=request.user)
        slot = DoctorAvailability.objects.get(id=slot_id, doctor=doctor)
        if slot.is_booked:
            return Response({"error": "Cannot delete a booked slot"}, status=400)
        slot.delete()
        return Response({"message": "Slot deleted"})
    except (Doctor.DoesNotExist, DoctorAvailability.DoesNotExist):
        return Response({"error": "Not found"}, status=404)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def bulk_delete_availability(request):
    try:
        doctor = Doctor.objects.get(user=request.user)
    except Doctor.DoesNotExist:
        return Response({"error": "Unauthorized"}, status=403)
    
    target_date = request.data.get('date')
    
    query = DoctorAvailability.objects.filter(doctor=doctor, is_booked=False)
    
    if target_date:
        query = query.filter(date=target_date)
    else:
        query = query.filter(date__gte=date.today())
    
    count = query.count()
    query.delete()
    
    return Response({"message": f"Successfully cleared {count} unbooked slots."})