from rest_framework import serializers
from .models import Baby, GrowthLog

class BabySerializer(serializers.ModelSerializer):
    class Meta:
        model = Baby
        fields = '__all__' 

    def validate_name(self,value):
        if len(value)<2:
            raise serializers.ValidationError("Baby name short")
        return value
class GrowthLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = GrowthLog
        fields = '__all__'  