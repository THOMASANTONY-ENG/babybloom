from datetime import timedelta
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from .models import VaccineSchedule
from parents.models import Baby


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def vaccine_reminders(request, baby_id):

    baby = Baby.objects.get(id=baby_id)

    schedules = VaccineSchedule.objects.all()

    reminders = []

    for vaccine in schedules:
        due_date = baby.dob + timedelta(days=vaccine.due_days)

        reminders.append(
            {
                "name": vaccine.name,
                "due_date": due_date,
            }
        )

    return Response(reminders)
