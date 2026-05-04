from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Baby
from .serializers import BabySerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import permission_classes


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_babies(request):
    babies = Baby.objects.filter(parent=request.user)
    serializer = BabySerializer(babies, many=True)
    return Response(serializer.data)  

from rest_framework import status

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_baby(request):
    data = request.data.copy()
    data["parent"] = request.user.id

    serializer = BabySerializer(data=data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)  

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_baby(request,baby_id):
    baby = Baby.objects.get(id=baby_id,parent=request.user)
    baby.delete()
    return Response({"message": "Baby deleted successfully"}) 
