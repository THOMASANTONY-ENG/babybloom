from django.contrib import admin
from .models import Resource

@admin.register(Resource)
class ResourceAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'recommended', 'created_at')
    list_filter = ('category', 'recommended')
    search_fields = ('title', 'content')
