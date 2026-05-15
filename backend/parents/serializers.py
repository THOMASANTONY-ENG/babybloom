from rest_framework import serializers
from .models import Baby, GrowthLog, CareNote


class BabySerializer(serializers.ModelSerializer):
    age = serializers.ReadOnlyField()

    class Meta:
        model = Baby
        fields = [
            'id', 'parent', 'name', 'dob', 'gender',
            'weight', 'height', 'blood_group', 'twins_group', 'age',
        ]
        read_only_fields = ['parent', 'age']

    def validate_name(self, value):
        if len(value) < 2:
            raise serializers.ValidationError("Baby name too short")
        return value


class GrowthLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = GrowthLog
        fields = '__all__'


class CareNoteSerializer(serializers.ModelSerializer):
    author_name = serializers.SerializerMethodField()

    class Meta:
        model = CareNote
        fields = [
            'id', 'baby', 'author', 'author_name',
            'category', 'title', 'content',
            'is_pinned', 'share_with_doctor',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['baby', 'author', 'author_name', 'created_at', 'updated_at']

    def get_author_name(self, obj):
        return obj.author.get_full_name() or obj.author.username