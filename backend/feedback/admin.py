from django.contrib import admin
from .models import Feedback

@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('user', 'feedback_type', 'category', 'rating', 'approved', 'created_at')
    list_filter = ('feedback_type', 'category', 'approved', 'rating')
    search_fields = ('user__username', 'message')
    actions = ['approve_testimonials']

    def approve_testimonials(self, request, queryset):
        queryset.update(approved=True)
    approve_testimonials.short_description = "Approve selected testimonials"
