from django.contrib import admin
from .models import Vaccine, VaccinationRecord, VaccineSchedule, BabyVaccine

admin.site.register(Vaccine)
admin.site.register(VaccinationRecord)
admin.site.register(VaccineSchedule)
admin.site.register(BabyVaccine)