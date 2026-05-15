from rest_framework import serializers
from .models import Feedback

class FeedbackSerializer(serializers.ModelSerializer):
    user_name = serializers.ReadOnlyField(source='user.username')
    
    class Meta:
        model = Feedback
        fields = ['id', 'user', 'user_name', 'feedback_type', 'category', 'message', 'rating', 'approved', 'created_at']
        read_only_fields = ['user']