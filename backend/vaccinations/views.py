from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Vaccine, VaccinationRecord
from parents.models import Baby
from accounts.views import admin_required


from django.shortcuts import redirect



@login_required
def vaccination_list(request, baby_id):
    baby = get_object_or_404(Baby, id=baby_id, parent=request.user)

    vaccines = Vaccine.objects.all()

    records = VaccinationRecord.objects.filter(baby=baby)

    completed = {r.vaccine.id: r.completed for r in records}

    return render(request, 'vaccinations/list.html', {
        'baby': baby,
        'vaccines': vaccines,
        'completed': completed
    })

    
@login_required
def mark_vaccine(request, baby_id, vaccine_id):
    baby = get_object_or_404(Baby, id=baby_id, parent=request.user)
    vaccine = get_object_or_404(Vaccine, id=vaccine_id)

    record, created = VaccinationRecord.objects.get_or_create(
        baby=baby,
        vaccine=vaccine
    )

    record.completed = True
    record.save()

    return redirect('vaccination_list', baby_id=baby.id)

@login_required
@admin_required
def vaccine_list(request):
    vaccines = Vaccine.objects.all()

    return render(request,'vaccinations/vaccine_list.html', {'vaccines': vaccines})

def add_vaccine(request):
    if request.method == "POST":
        name = request.POST['name']

        age = request.POST['recommended_age']

        Vaccine.objects.create(
            name = name,
            recommended_age = age
        )
        return redirect('vaccine_list')
    else:
        return render(request, 'vaccinations/add_vaccine.html')


@login_required
@admin_required
def delete_vaccine(request, vaccine_id):
    vaccine = get_object_or_404(Vaccine, id=vaccine_id)

    if VaccinationRecord.objects.filter(vaccine=vaccine).exists():
        return redirect('vaccine_list')  
    vaccine.delete()

    return redirect('vaccine_list')