from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Feedback
from .serializers import FeedbackSerializer

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_feedback(request):
    serializer = FeedbackSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(user=request.user)
        return Response(serializer.data, status=201)
    return Response(serializer.errors, status=400)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def all_feedbacks(request):
    # Only allow doctors/admins to see all feedback if needed, 
    # but specifically admins for management
    if request.user.profile.role != 'admin':
        return Response({"error": "Unauthorized"}, status=403)
    
    feedbacks = Feedback.objects.all().order_by('-created_at')
    serializer = FeedbackSerializer(feedbacks, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def private_feedbacks(request):
    feedbacks = Feedback.objects.filter(feedback_type='private').order_by('-created_at')
    serializer = FeedbackSerializer(feedbacks, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def approved_testimonials(request):
    testimonials = Feedback.objects.filter(feedback_type='testimonial', approved=True).order_by('-created_at')
    serializer = FeedbackSerializer(testimonials, many=True)
    return Response(serializer.data)

@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def approve_testimonial(request, feedback_id):
    try:
        feedback = Feedback.objects.get(id=feedback_id)
        feedback.approved = True
        feedback.save()
        return Response({"message": "Approved"})
    except Feedback.DoesNotExist:
        return Response({"error": "Not found"}, status=404)