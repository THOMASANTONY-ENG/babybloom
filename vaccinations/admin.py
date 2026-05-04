from django.contrib import admin
from .models import Vaccine, VaccinationRecord

admin.site.register(Vaccine)
admin.site.register(VaccinationRecord)