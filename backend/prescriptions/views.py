from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from appointments.models import Appointment
from .models import Prescription
from doctors.models import Doctor


@login_required
def add_prescription(request, appointment_id):
    # Ensure user is a doctor
    try:
        doctor = Doctor.objects.get(user=request.user)
    except Doctor.DoesNotExist:
        return redirect('home')

    appointment = get_object_or_404(
        Appointment,
        id=appointment_id,
        doctor=doctor
    )

    if appointment.status != 'completed':
        return redirect('doctor_appointments')

    if request.method == 'POST':
        medication = request.POST['medication']
        dosage = request.POST['dosage']
        instructions = request.POST['instructions']

        # Update or create prescription
        Prescription.objects.update_or_create(
            appointment=appointment,
            defaults={
                'medication': medication,
                'dosage': dosage,
                'instructions': instructions
            }
        )

        return redirect('doctor_appointments')

    return render(request, 'prescriptions/add.html', {
        'appointment': appointment
    })

@login_required
def view_prescription(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)
    
    if appointment.baby.parent != request.user:
        return redirect('home')

    prescription = get_object_or_404(Prescription, appointment=appointment)
    
    return render(request, 'prescriptions/view.html', {
        'prescription': prescription,
        'appointment': appointment
    })
@login_required
def view_prescriptions(request):

    prescriptions = Prescription.objects.filter(
        appointment__baby__parent=request.user
    )
    return render(request, 'prescriptions/list.html', {
        'prescriptions': prescriptions
    })

    