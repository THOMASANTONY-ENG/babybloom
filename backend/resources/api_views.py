from rest_framework.decorators import (
    api_view,
    permission_classes
)

from rest_framework.permissions import (
    IsAuthenticated
)

from rest_framework.response import Response

from .models import Resource

from .serializers import ResourceSerializer

from .permissions import IsDoctorOrAdmin

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def resources_list(request):
    resources = Resource.objects.all().order_by('-created_at')
    serializer = ResourceSerializer(resources, many=True)
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([IsAuthenticated, IsDoctorOrAdmin])
def create_resource(request):
    serializer = ResourceSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=201)
    return Response(serializer.errors, status=400)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def recommended_resources(request):
    resources = Resource.objects.filter(recommended=True)
    serializer = ResourceSerializer(resources, many=True)
    return Response(serializer.data)