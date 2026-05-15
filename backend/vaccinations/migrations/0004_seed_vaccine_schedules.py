from django.db import migrations

# Standard WHO / National Immunization Schedule mapped to days after birth
STANDARD_VACCINES = [
    # Milestone: Birth (day 0)
    ("BCG (Tuberculosis)", 0),
    ("Hepatitis B (Birth dose)", 0),
    ("OPV 0 (Oral Polio Vaccine)", 0),

    # Milestone: 6 Weeks (42 days)
    ("DTP 1 (Diphtheria, Tetanus, Pertussis)", 42),
    ("IPV 1 (Inactivated Polio)", 42),
    ("Hib 1 (Haemophilus influenzae type b)", 42),
    ("PCV 1 (Pneumococcal Conjugate)", 42),
    ("Rotavirus 1", 42),
    ("Hepatitis B 2", 42),

    # Milestone: 10 Weeks (70 days)
    ("DTP 2", 70),
    ("IPV 2", 70),
    ("Hib 2", 70),
    ("PCV 2", 70),
    ("Rotavirus 2", 70),
    ("Hepatitis B 3", 70),

    # Milestone: 14 Weeks (98 days)
    ("DTP 3", 98),
    ("IPV 3", 98),
    ("Hib 3", 98),
    ("PCV 3", 98),
    ("Rotavirus 3", 98),

    # Milestone: 6 Months (180 days)
    ("OPV 1", 180),
    ("Influenza 1", 180),

    # Milestone: 9 Months (270 days)
    ("MMR 1 (Measles, Mumps, Rubella)", 270),
    ("OPV 2", 270),

    # Milestone: 12 Months (365 days)
    ("Hepatitis A 1", 365),
    ("Varicella (Chickenpox) 1", 365),
    ("PCV Booster", 365),

    # Milestone: 15 Months (456 days)
    ("MMR 2", 456),
    ("Varicella 2", 456),

    # Milestone: 18 Months (548 days)
    ("DTP Booster 1", 548),
    ("Hepatitis A 2", 548),
    ("OPV 3", 548),

    # Milestone: 2 Years (730 days)
    ("Typhoid Conjugate Vaccine", 730),

    # Milestone: 4-6 Years (1825 days)
    ("DTP Booster 2", 1825),
    ("OPV 4", 1825),
    ("MMR 3", 1825),
]


def seed_vaccines(apps, schema_editor):
    VaccineSchedule = apps.get_model("vaccinations", "VaccineSchedule")
    existing_names = set(VaccineSchedule.objects.values_list("name", flat=True))
    to_create = [
        VaccineSchedule(name=name, due_days=days)
        for name, days in STANDARD_VACCINES
        if name not in existing_names
    ]
    if to_create:
        VaccineSchedule.objects.bulk_create(to_create)


def unseed_vaccines(apps, schema_editor):
    VaccineSchedule = apps.get_model("vaccinations", "VaccineSchedule")
    names = [name for name, _ in STANDARD_VACCINES]
    VaccineSchedule.objects.filter(name__in=names).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("vaccinations", "0003_babyvaccine_administered_by_babyvaccine_batch_number_and_more"),
    ]

    operations = [
        migrations.RunPython(seed_vaccines, reverse_code=unseed_vaccines),
    ]
