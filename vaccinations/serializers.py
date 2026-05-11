from rest_framework import serializers
from .models import BabyVaccine

class BabyVaccineSerializer(serializers.ModelSerializer):
    class Meta:
        model = BabyVaccine
        fields = '__all__'
