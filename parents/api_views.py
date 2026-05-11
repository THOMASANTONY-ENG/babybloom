from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Baby, GrowthLog
from .serializers import BabySerializer, GrowthLogSerializer
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
        baby = serializer.save()
        GrowthLog.objects.create(
            baby=baby,
            weight=baby.weight,
            height=baby.height
        )
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)  

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_baby(request,baby_id):
    baby = Baby.objects.get(id=baby_id,parent=request.user)
    baby.delete()
    return Response({"message": "Baby deleted successfully"}) 

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def growth_records(request, baby_id):
    records = GrowthLog.objects.filter(baby_id=baby_id).order_by('date', 'id')

    serializer = GrowthLogSerializer(records, many=True)
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_growth(request, baby_id):
    try:
        baby = Baby.objects.get(id=baby_id, parent=request.user)
    except Baby.DoesNotExist:
        return Response({"detail": "Baby not found."}, status=status.HTTP_404_NOT_FOUND)
        
    data = request.data.copy()
    data["baby"] = baby.id
    
    serializer = GrowthLogSerializer(data=data)
    if serializer.is_valid():
        growth_log = serializer.save()
        baby.weight = growth_log.weight
        baby.height = growth_log.height
        baby.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)