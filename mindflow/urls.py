from django.urls import path
from . import views

app_name = 'mindflow'

urlpatterns = [
    # Dashboard
    path('', views.dashboard, name='dashboard'),

    # Capture
    path('capture/', views.capture_note, name='capture'),
    path('capture/quick/', views.quick_capture, name='quick_capture'),
    path('capture/process/<int:note_id>/', views.process_note, name='process_note'),

    # Notes
    path('notes/', views.note_list, name='note_list'),
    path('notes/<int:note_id>/', views.note_detail, name='note_detail'),
    path('notes/<int:note_id>/archive/', views.archive_note, name='archive_note'),

    # Energy/Mood
    path('energy/check-in/', views.energy_checkin, name='energy_checkin'),

    # Categories
    path('organize/<slug:category_slug>/', views.organize_category, name='organize_category'),

    # Plans
    path('plans/', views.plan_list, name='plan_list'),
    path('plans/create/', views.create_plan, name='create_plan'),
    path('plans/<int:plan_id>/', views.plan_detail, name='plan_detail'),
    path('plans/<int:plan_id>/step/<int:step_id>/complete/', views.complete_step, name='complete_step'),
    path('plans/<int:plan_id>/step/<int:step_id>/start/', views.start_step, name='start_step'),

    # Settings
    path('settings/profile/', views.neuro_profile_settings, name='neuro_profile_settings'),

    # HTMX partials
    path('partials/recent-notes/', views.partial_recent_notes, name='partial_recent_notes'),
    path('partials/thought-garden/', views.partial_thought_garden, name='partial_thought_garden'),
    path('partials/active-plans/', views.partial_active_plans, name='partial_active_plans'),
]
