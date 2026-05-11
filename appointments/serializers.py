from rest_framework import serializers
from .models import Appointment
from prescriptions.models import Prescription

class AppointmentSerializer(serializers.ModelSerializer):
    has_prescription = serializers.SerializerMethodField()

    class Meta:
        model = Appointment
        fields = '__all__'

    def get_has_prescription(self, obj):
        return Prescription.objects.filter(appointment=obj).exists()