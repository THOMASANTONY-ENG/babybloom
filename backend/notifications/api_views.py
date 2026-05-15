from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from .utils import send_vaccine_reminders, send_appointment_reminders

@api_view(['GET'])
@permission_classes([IsAdminUser]) # Restrict to admins for safety
def send_all_reminders(request):
    """Manual trigger for sending all pending notification emails."""
    vax_sent = send_vaccine_reminders()
    appt_sent = send_appointment_reminders()
    
    return Response({
        "status": "success",
        "message": "Reminders processed",
        "vaccine_emails_sent": vax_sent,
        "appointment_emails_sent": appt_sent
    })