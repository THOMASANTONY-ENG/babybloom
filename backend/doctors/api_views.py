from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Doctor

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_doctors_api(request):
    doctors = Doctor.objects.all()
    data = [{
        "id": d.id,
        "name": f"Dr. {d.user.username}",
        "speciality": d.speciality,
        "experience": d.experience
    } for d in doctors]
    return Response(data)
