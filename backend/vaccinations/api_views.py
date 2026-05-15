from datetime import timedelta, date
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework import status as http_status
from django.shortcuts import get_object_or_404

from .models import VaccineSchedule, BabyVaccine
from parents.models import Baby


# ─── Helpers ───────────────────────────────────────────────────────────────────

def _days_to_label(days: int) -> str:
    """Convert due_days into a human-readable milestone label."""
    if days == 0:
        return "Birth"
    if days % 365 == 0:
        years = days // 365
        return f"{years} Year{'s' if years > 1 else ''}"
    if days % 30 == 0:
        months = days // 30
        return f"{months} Month{'s' if months > 1 else ''}"
    weeks = days // 7
    if days % 7 == 0:
        return f"{weeks} Week{'s' if weeks > 1 else ''}"
    # Fall back to days
    return f"{days} Days"


def _urgency(days_until: int, completed: bool) -> str:
    """Return urgency level: 'completed', 'overdue', 'imminent', 'upcoming', 'future'."""
    if completed:
        return "completed"
    if days_until < 0:
        return "overdue"
    if days_until <= 7:
        return "imminent"
    if days_until <= 30:
        return "upcoming"
    return "future"


def _build_reminder(schedule, record, today, dob):
    due_date = dob + timedelta(days=schedule.due_days)
    days_until = (due_date - today).days
    completed = record.completed if record else False

    vaccine_status = "pending"
    if completed:
        vaccine_status = "completed"
    elif due_date < today:
        vaccine_status = "overdue"

    return {
        "record_id": record.id if record else None,
        "id": schedule.id,
        "name": schedule.name,
        "due_days": schedule.due_days,
        "milestone_label": _days_to_label(schedule.due_days),
        "due_date": due_date.isoformat(),
        "days_until_due": days_until,
        "urgency": _urgency(days_until, completed),
        "status": vaccine_status,
        "completed": completed,
        "batch_number": record.batch_number if record else None,
        "administered_by": record.administered_by.get_full_name() or record.administered_by.username
                           if record and record.administered_by else None,
        "notes": record.notes if record else None,
        "date_given": record.date_given.isoformat() if record and record.date_given else None,
    }


# ─── Per-baby Reminders ────────────────────────────────────────────────────────

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def vaccine_reminders(request, baby_id):
    try:
        baby = Baby.objects.get(id=baby_id)
    except Baby.DoesNotExist:
        return Response({"error": "Baby not found"}, status=404)

    schedules = VaccineSchedule.objects.all().order_by("due_days")
    today = date.today()
    reminders = []

    for schedule in schedules:
        record = BabyVaccine.objects.filter(baby=baby, vaccine=schedule).first()
        if not record:
            record = BabyVaccine.objects.create(baby=baby, vaccine=schedule)
        reminders.append(_build_reminder(schedule, record, today, baby.dob))

    return Response(reminders)


# ─── Milestone Timeline (grouped by milestone label) ──────────────────────────

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def vaccine_milestone_timeline(request, baby_id):
    """
    Returns vaccines grouped by milestone label, sorted chronologically.
    Also computes a 'next_milestone' block showing the soonest pending group.
    """
    try:
        baby = Baby.objects.get(id=baby_id)
    except Baby.DoesNotExist:
        return Response({"error": "Baby not found"}, status=404)

    schedules = VaccineSchedule.objects.all().order_by("due_days")
    today = date.today()

    # Build grouped dict: {due_days -> {label, due_date, vaccines[]}}
    groups: dict = {}
    for schedule in schedules:
        record = BabyVaccine.objects.filter(baby=baby, vaccine=schedule).first()
        if not record:
            record = BabyVaccine.objects.create(baby=baby, vaccine=schedule)

        reminder = _build_reminder(schedule, record, today, baby.dob)
        key = schedule.due_days

        if key not in groups:
            due_date = baby.dob + timedelta(days=schedule.due_days)
            days_until = (due_date - today).days
            groups[key] = {
                "due_days": key,
                "milestone_label": _days_to_label(key),
                "due_date": due_date.isoformat(),
                "days_until_due": days_until,
                "vaccines": [],
            }
        groups[key]["vaccines"].append(reminder)

    # Sort groups chronologically
    sorted_groups = sorted(groups.values(), key=lambda g: g["due_days"])

    # Compute aggregate status for each group
    for g in sorted_groups:
        all_completed = all(v["completed"] for v in g["vaccines"])
        any_overdue = any(v["status"] == "overdue" for v in g["vaccines"])
        any_imminent = any(v["urgency"] == "imminent" for v in g["vaccines"])

        if all_completed:
            g["group_status"] = "completed"
        elif any_overdue:
            g["group_status"] = "overdue"
        elif any_imminent:
            g["group_status"] = "imminent"
        elif g["days_until_due"] >= 0:
            g["group_status"] = "upcoming"
        else:
            g["group_status"] = "overdue"

    # Find next pending milestone (first non-completed group in the future or overdue)
    next_milestone = None
    for g in sorted_groups:
        if g["group_status"] != "completed":
            next_milestone = g
            break

    # Summary stats
    all_vaccines = [v for g in sorted_groups for v in g["vaccines"]]
    total = len(all_vaccines)
    done = sum(1 for v in all_vaccines if v["completed"])
    overdue_count = sum(1 for v in all_vaccines if v["status"] == "overdue")

    return Response({
        "baby_id": baby.id,
        "baby_name": baby.name,
        "baby_dob": baby.dob.isoformat(),
        "baby_age": baby.age,
        "summary": {
            "total": total,
            "completed": done,
            "pending": total - done,
            "overdue": overdue_count,
            "progress_pct": round((done / total * 100)) if total else 0,
        },
        "next_milestone": next_milestone,
        "timeline": sorted_groups,
    })


# ─── All Babies Reminders (for calendar / doctor view) ────────────────────────

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def all_vaccination_reminders(request):
    babies = Baby.objects.all()
    schedules = VaccineSchedule.objects.all()
    all_events = []

    for baby in babies:
        for schedule in schedules:
            due_date = baby.dob + timedelta(days=schedule.due_days)
            record = BabyVaccine.objects.filter(baby=baby, vaccine=schedule).first()

            vaccine_status = "pending"
            if record and record.completed:
                vaccine_status = "completed"
            elif due_date < date.today():
                vaccine_status = "overdue"

            if vaccine_status != "completed":
                all_events.append({
                    "id": f"v-{baby.id}-{schedule.id}",
                    "baby_name": baby.name,
                    "name": schedule.name,
                    "milestone_label": _days_to_label(schedule.due_days),
                    "date": due_date.isoformat(),
                    "days_until_due": (due_date - date.today()).days,
                    "status": vaccine_status,
                    "type": "vaccination",
                })

    # Sort by date ascending
    all_events.sort(key=lambda e: e["date"])
    return Response(all_events)


# ─── Admin: Manage Schedules ──────────────────────────────────────────────────

@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def manage_vaccine_schedules(request):
    if request.user.profile.role != "admin":
        return Response({"error": "Unauthorized"}, status=403)

    if request.method == "GET":
        schedules = VaccineSchedule.objects.all().order_by("due_days")
        data = [
            {
                "id": s.id,
                "name": s.name,
                "due_days": s.due_days,
                "milestone_label": _days_to_label(s.due_days),
            }
            for s in schedules
        ]
        return Response(data)

    elif request.method == "POST":
        name = request.data.get("name")
        due_days = request.data.get("due_days")
        if not name or due_days is None:
            return Response({"error": "name and due_days are required"}, status=400)
        schedule = VaccineSchedule.objects.create(name=name, due_days=int(due_days))
        return Response(
            {"id": schedule.id, "name": schedule.name, "due_days": schedule.due_days,
             "milestone_label": _days_to_label(schedule.due_days)},
            status=201,
        )


@api_view(["PUT", "DELETE"])
@permission_classes([IsAuthenticated])
def modify_vaccine_schedule(request, pk):
    if request.user.profile.role != "admin":
        return Response({"error": "Unauthorized"}, status=403)

    schedule = get_object_or_404(VaccineSchedule, pk=pk)

    if request.method == "PUT":
        schedule.name = request.data.get("name", schedule.name)
        schedule.due_days = int(request.data.get("due_days", schedule.due_days))
        schedule.save()
        return Response({
            "id": schedule.id, "name": schedule.name,
            "due_days": schedule.due_days,
            "milestone_label": _days_to_label(schedule.due_days),
        })

    elif request.method == "DELETE":
        schedule.delete()
        return Response({"message": "Deleted"})


# ─── Doctor / Admin: Mark Vaccine Administered ────────────────────────────────

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def update_baby_vaccine(request, record_id):
    if request.user.profile.role not in ["doctor", "admin"]:
        return Response({"error": "Unauthorized"}, status=403)

    record = get_object_or_404(BabyVaccine, id=record_id)

    record.completed = True
    record.date_given = date.today()
    record.batch_number = request.data.get("batch_number")
    record.administered_by = request.user
    record.notes = request.data.get("notes")
    record.save()

    return Response({"message": "Vaccine record updated successfully"})
