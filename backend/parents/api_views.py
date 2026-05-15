import uuid as uuid_lib
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from .models import Baby, GrowthLog, CareNote
from .serializers import BabySerializer, GrowthLogSerializer, CareNoteSerializer
from vaccinations.models import BabyVaccine, VaccineSchedule


# ─── Helpers ───────────────────────────────────────────────────────────────────

def _init_baby(baby: Baby):
    """Create first growth log and auto-assign all vaccine schedules."""
    GrowthLog.objects.create(baby=baby, weight=baby.weight, height=baby.height)
    for schedule in VaccineSchedule.objects.all():
        BabyVaccine.objects.get_or_create(baby=baby, vaccine=schedule, defaults={"completed": False})


# ─── List / Get ────────────────────────────────────────────────────────────────

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_babies(request):
    babies = Baby.objects.filter(parent=request.user)
    serializer = BabySerializer(babies, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_baby(request, baby_id):
    try:
        baby = Baby.objects.get(id=baby_id)
        # Parents can only view their own babies; doctors/admins bypass
        user_role = getattr(getattr(request.user, 'profile', None), 'role', 'parent')
        if baby.parent != request.user and user_role == 'parent':
            return Response({"error": "Unauthorized"}, status=status.HTTP_403_FORBIDDEN)
        serializer = BabySerializer(baby)
        return Response(serializer.data)
    except Baby.DoesNotExist:
        return Response({"error": "Baby not found"}, status=status.HTTP_404_NOT_FOUND)


# ─── Create ────────────────────────────────────────────────────────────────────

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_baby(request):
    data = request.data.copy()
    data["parent"] = request.user.id

    serializer = BabySerializer(data=data)
    if serializer.is_valid():
        baby = serializer.save(parent=request.user)
        _init_baby(baby)
        return Response(BabySerializer(baby).data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_twins(request):
    """
    Accepts a list of exactly 2 baby objects and creates them linked as twins
    via a shared twins_group UUID.
    Expected body: { "babies": [ {...baby1 fields...}, {...baby2 fields...} ] }
    """
    babies_data = request.data.get("babies", [])
    if len(babies_data) != 2:
        return Response({"error": "Exactly 2 babies are required for twins."}, status=status.HTTP_400_BAD_REQUEST)

    group_id = str(uuid_lib.uuid4())
    created = []
    errors = []

    for baby_data in babies_data:
        data = baby_data.copy()
        data["parent"] = request.user.id
        data["twins_group"] = group_id
        serializer = BabySerializer(data=data)
        if serializer.is_valid():
            baby = serializer.save(parent=request.user)
            _init_baby(baby)
            created.append(BabySerializer(baby).data)
        else:
            errors.append(serializer.errors)

    if errors:
        # Roll back created babies
        Baby.objects.filter(twins_group=group_id).delete()
        return Response({"errors": errors}, status=status.HTTP_400_BAD_REQUEST)

    return Response({"twins_group": group_id, "babies": created}, status=status.HTTP_201_CREATED)


# ─── Update ────────────────────────────────────────────────────────────────────

@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def update_baby(request, baby_id):
    try:
        baby = Baby.objects.get(id=baby_id, parent=request.user)
    except Baby.DoesNotExist:
        return Response({"error": "Baby not found or unauthorized"}, status=status.HTTP_404_NOT_FOUND)

    serializer = BabySerializer(baby, data=request.data, partial=True)
    if serializer.is_valid():
        baby = serializer.save()
        return Response(BabySerializer(baby).data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ─── Delete ────────────────────────────────────────────────────────────────────

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_baby(request, baby_id):
    try:
        baby = Baby.objects.get(id=baby_id, parent=request.user)
    except Baby.DoesNotExist:
        return Response({"error": "Not found"}, status=status.HTTP_404_NOT_FOUND)
    baby.delete()
    return Response({"message": "Baby deleted successfully"})


# ─── Growth ────────────────────────────────────────────────────────────────────

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def growth_records(request, baby_id):
    records = GrowthLog.objects.filter(baby_id=baby_id).order_by('date', 'id')
    serializer = GrowthLogSerializer(records, many=True)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_growth(request, baby_id):
    try:
        baby = Baby.objects.get(id=baby_id, parent=request.user)
    except Baby.DoesNotExist:
        return Response({"detail": "Baby not found."}, status=status.HTTP_404_NOT_FOUND)

    data = request.data.copy()
    data["baby"] = baby.id

    serializer = GrowthLogSerializer(data=data)
    if serializer.is_valid():
        growth_log = serializer.save()
        # Keep baby's latest vitals in sync
        baby.weight = growth_log.weight
        baby.height = growth_log.height
        baby.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ─── Care Notes ────────────────────────────────────────────────────────────────

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_care_notes(request, baby_id):
    """
    List care notes for a baby.
    Doctors/admins see only notes flagged share_with_doctor=True.
    Parents see all their own notes.
    Query params:
      ?category=symptom
      ?shared_only=1   (force only shared)
      ?pinned_only=1
    """
    try:
        baby = Baby.objects.get(id=baby_id)
    except Baby.DoesNotExist:
        return Response({'error': 'Baby not found'}, status=status.HTTP_404_NOT_FOUND)

    user_role = getattr(getattr(request.user, 'profile', None), 'role', 'parent')

    if user_role == 'parent':
        if baby.parent != request.user:
            return Response({'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)
        notes = CareNote.objects.filter(baby=baby)
    else:
        # Doctors / admins see only shared notes
        notes = CareNote.objects.filter(baby=baby, share_with_doctor=True)

    # Optional filters
    category = request.GET.get('category')
    if category:
        notes = notes.filter(category=category)
    if request.GET.get('shared_only') == '1':
        notes = notes.filter(share_with_doctor=True)
    if request.GET.get('pinned_only') == '1':
        notes = notes.filter(is_pinned=True)

    serializer = CareNoteSerializer(notes, many=True)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_care_note(request, baby_id):
    try:
        baby = Baby.objects.get(id=baby_id, parent=request.user)
    except Baby.DoesNotExist:
        return Response({'error': 'Baby not found'}, status=status.HTTP_404_NOT_FOUND)

    serializer = CareNoteSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(baby=baby, author=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def update_care_note(request, note_id):
    try:
        note = CareNote.objects.get(id=note_id, author=request.user)
    except CareNote.DoesNotExist:
        return Response({'error': 'Note not found'}, status=status.HTTP_404_NOT_FOUND)

    serializer = CareNoteSerializer(note, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_care_note(request, note_id):
    try:
        note = CareNote.objects.get(id=note_id, author=request.user)
    except CareNote.DoesNotExist:
        return Response({'error': 'Note not found'}, status=status.HTTP_404_NOT_FOUND)
    note.delete()
    return Response({'message': 'Note deleted'})


@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def toggle_pin_note(request, note_id):
    try:
        note = CareNote.objects.get(id=note_id, author=request.user)
    except CareNote.DoesNotExist:
        return Response({'error': 'Note not found'}, status=status.HTTP_404_NOT_FOUND)
    note.is_pinned = not note.is_pinned
    note.save()
    return Response({'is_pinned': note.is_pinned})


@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def toggle_share_note(request, note_id):
    try:
        note = CareNote.objects.get(id=note_id, author=request.user)
    except CareNote.DoesNotExist:
        return Response({'error': 'Note not found'}, status=status.HTTP_404_NOT_FOUND)
    note.share_with_doctor = not note.share_with_doctor
    note.save()
    return Response({'share_with_doctor': note.share_with_doctor})