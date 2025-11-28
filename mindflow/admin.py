from django.contrib import admin
from .models import NeuroProfile, MoodCheckIn, Category, Note, Plan, Step, Celebration


@admin.register(NeuroProfile)
class NeuroProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'attention_span_preference', 'tracks_energy_levels', 'created_at']
    list_filter = ['attention_span_preference', 'tracks_energy_levels', 'prefers_minimal_motion']
    search_fields = ['user__email']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(MoodCheckIn)
class MoodCheckInAdmin(admin.ModelAdmin):
    list_display = ['user', 'energy_level', 'overwhelm_level', 'focus_quality', 'timestamp']
    list_filter = ['energy_level', 'focus_quality', 'timestamp']
    search_fields = ['user__email', 'notes']
    readonly_fields = ['timestamp']
    date_hierarchy = 'timestamp'


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'color', 'is_system', 'user', 'created_at']
    list_filter = ['is_system', 'created_at']
    search_fields = ['name', 'slug', 'description']
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ['created_at']


@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):
    list_display = ['user', 'content_preview', 'category', 'status', 'energy_impact', 'is_actionable', 'created_at']
    list_filter = ['status', 'energy_impact', 'is_actionable', 'category', 'created_at']
    search_fields = ['user__email', 'content', 'processed_content', 'tags']
    readonly_fields = ['created_at', 'updated_at', 'processed_at', 'archived_at', 'embedding_id']
    date_hierarchy = 'created_at'

    fieldsets = (
        ('Core Content', {
            'fields': ('user', 'content', 'processed_content', 'status')
        }),
        ('AI Analysis', {
            'fields': ('validation_message', 'gentle_reframe', 'category', 'tags')
        }),
        ('Energy & Actionability', {
            'fields': ('energy_impact', 'is_actionable', 'actionable_items', 'processing_items')
        }),
        ('Context', {
            'fields': ('captured_at_energy', 'location_context', 'time_context')
        }),
        ('Metadata', {
            'fields': ('embedding_id', 'created_at', 'updated_at', 'processed_at', 'archived_at'),
            'classes': ('collapse',)
        }),
    )

    def content_preview(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    content_preview.short_description = 'Content'


class StepInline(admin.TabularInline):
    model = Step
    extra = 0
    fields = ['order', 'title', 'energy_cost', 'estimated_minutes', 'status']
    readonly_fields = []


@admin.register(Plan)
class PlanAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'status', 'recommended_energy', 'completion_percentage', 'created_at']
    list_filter = ['status', 'recommended_energy', 'created_at']
    search_fields = ['user__email', 'title', 'description']
    readonly_fields = ['total_steps', 'completed_steps', 'created_at', 'updated_at', 'started_at', 'completed_at']
    date_hierarchy = 'created_at'
    filter_horizontal = ['source_notes']
    inlines = [StepInline]

    fieldsets = (
        ('Plan Details', {
            'fields': ('user', 'title', 'description', 'status', 'recommended_energy')
        }),
        ('Source', {
            'fields': ('source_notes',)
        }),
        ('Progress', {
            'fields': ('total_steps', 'completed_steps')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'started_at', 'completed_at'),
            'classes': ('collapse',)
        }),
    )

    def completion_percentage(self, obj):
        return f"{obj.get_completion_percentage()}%"
    completion_percentage.short_description = 'Progress'


@admin.register(Step)
class StepAdmin(admin.ModelAdmin):
    list_display = ['title', 'plan', 'order', 'energy_cost', 'estimated_minutes', 'status', 'created_at']
    list_filter = ['status', 'energy_cost', 'plan__user', 'created_at']
    search_fields = ['title', 'description', 'plan__title']
    readonly_fields = ['created_at', 'started_at', 'completed_at']
    date_hierarchy = 'created_at'

    fieldsets = (
        ('Step Details', {
            'fields': ('plan', 'order', 'title', 'description')
        }),
        ('Tasks', {
            'fields': ('micro_tasks',)
        }),
        ('Effort', {
            'fields': ('energy_cost', 'estimated_minutes')
        }),
        ('Status', {
            'fields': ('status', 'created_at', 'started_at', 'completed_at')
        }),
    )


@admin.register(Celebration)
class CelebrationAdmin(admin.ModelAdmin):
    list_display = ['user', 'celebration_type', 'message', 'viewed', 'created_at']
    list_filter = ['celebration_type', 'viewed', 'created_at']
    search_fields = ['user__email', 'message']
    readonly_fields = ['created_at']
    date_hierarchy = 'created_at'
