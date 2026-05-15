from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import ContactMessage
from .serializers import ContactMessageSerializer

@api_view(['POST'])
def create_contact_message(request):
    serializer = ContactMessageSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=201)
    return Response(serializer.errors, status=400)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def admin_inbox(request):
    if request.user.profile.role != 'admin':
        return Response({"error": "Unauthorized"}, status=403)
    
    messages = ContactMessage.objects.all().order_by('-created_at')
    serializer = ContactMessageSerializer(messages, many=True)
    return Response(serializer.data)

@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def resolve_message(request, message_id):
    if request.user.profile.role != 'admin':
        return Response({"error": "Unauthorized"}, status=403)
        
    try:
        message = ContactMessage.objects.get(id=message_id)
        message.status = 'resolved'
        message.save()
        return Response({"message": "Resolved"})
    except ContactMessage.DoesNotExist:
        return Response({"error": "Not found"}, status=404)