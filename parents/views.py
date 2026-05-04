from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Baby,GrowthLog


# Create your views here.
@login_required
def add_baby(request):
    if request.method == "POST":
        name = request.POST['name']
        dob = request.POST['dob']
        gender = request.POST['gender']
        weight = request.POST['weight']
        height = request.POST['height']

        Baby.objects.create(
            parent = request.user,
            name = name,
            dob = dob,
            gender = gender,
            weight = weight,
            height = height
        )
        return redirect('view_babies')
    return render(request, 'parents/add_baby.html')
        
@login_required
def view_babies(request):
    babies = Baby.objects.filter(parent=request.user)
    return render(request, 'parents/view_babies.html', {'babies': babies})

@login_required
def edit_baby(request,baby_id):
    baby = get_object_or_404(Baby,id=baby_id,parent=request.user)
    
    if request.method == "POST":
        baby.name = request.POST['name']
        baby.dob = request.POST['dob']
        baby.gender = request.POST['gender']
        baby.weight = request.POST['weight']
        baby.height = request.POST['height']
        baby.save()
        return redirect('view_babies')

    return render(request,'parents/edit_baby.html',{'baby':baby})
    
@login_required
def delete_baby(request, baby_id):
    baby = get_object_or_404(Baby, id=baby_id, parent=request.user)

    if request.method == 'POST':
        baby.delete()
        return redirect('view_babies')

    return render(request, 'parents/delete_baby.html', {'baby': baby})
@login_required
def add_growth(request,baby_id):
    baby = get_object_or_404(Baby,id = baby_id, parent = request.user)
    if request.method == "POST":

        weight = request.POST["weight"]
        height = request.POST["height"]
        # notes = request.POST["notes"]
        GrowthLog.objects.create(
            baby = baby,
            weight = weight,
            height = height,
            # notes = notes
        )
        return redirect('view_growth', baby_id=baby_id)
    return render(request, 'parents/add_growth.html', {'baby': baby})
@login_required
def view_growth(request,baby_id):
    baby = get_object_or_404(Baby,id=baby_id,parent=request.user)
    logs = GrowthLog.objects.filter(baby=baby).order_by('date')
    return render(request,'parents/view_growth.html',{'baby':baby,'logs':logs})
