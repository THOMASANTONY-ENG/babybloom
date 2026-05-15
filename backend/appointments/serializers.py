from rest_framework import serializers
from .models import Appointment, DoctorAvailability
from prescriptions.models import Prescription

class AppointmentSerializer(serializers.ModelSerializer):
    has_prescription = serializers.SerializerMethodField()
    baby_name = serializers.CharField(source='baby.name', read_only=True)

    class Meta:
        model = Appointment
        fields = '__all__'

    def get_has_prescription(self, obj):
        return Prescription.objects.filter(appointment=obj).exists()

class DoctorAvailabilitySerializer(
    serializers.ModelSerializer
):

    class Meta:

        model = DoctorAvailability

        fields = '__all__'