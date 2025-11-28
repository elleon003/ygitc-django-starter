from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.db.models import Count, Q, Prefetch
from django.conf import settings
from django.utils import timezone
from django.views.decorators.http import require_http_methods
from django.core.paginator import Paginator

from .models import Note, Category, Plan, Step, MoodCheckIn, NeuroProfile, Celebration
from .services import EmpathicAIProcessor, NeuroFriendlyFeatures
from .forms import NoteForm, EnergyCheckInForm, NeuroProfileForm, PlanForm

import logging

logger = logging.getLogger(__name__)


@login_required
def dashboard(request):
    """Main dashboard with thought garden and active plans - optimized queries"""
    user = request.user

    # Get or create neuro profile
    neuro_profile, _ = NeuroProfile.objects.get_or_create(user=user)

    # Get recent mood check-in
    latest_mood = MoodCheckIn.objects.filter(user=user).first()

    # Get recent notes with category (prevent N+1)
    recent_notes = Note.objects.filter(
        user=user,
        status__in=['captured', 'processing', 'processed']
    ).select_related('category').order_by('-created_at')[:settings.MINDFLOW_RECENT_NOTES_COUNT]

    # Get thought garden categories with note counts (prevent N+1)
    categories_with_counts = Category.objects.filter(
        Q(user=user) | Q(is_system=True)
    ).annotate(
        note_count=Count('notes', filter=Q(notes__user=user, notes__status__in=['captured', 'processed']))
    ).filter(note_count__gt=0).order_by('-note_count')

    # Get active plans with progress (prevent N+1 with prefetch)
    active_plans = Plan.objects.filter(
        user=user,
        status='active'
    ).prefetch_related(
        Prefetch('steps', queryset=Step.objects.order_by('order'))
    ).order_by('-updated_at')[:settings.MINDFLOW_MAX_ACTIVE_PLANS]

    # Calculate completion for each plan
    for plan in active_plans:
        plan.completion_percentage = plan.get_completion_percentage()
        plan.next_step_obj = plan.get_next_step()

    # Get unviewed celebrations
    celebrations = Celebration.objects.filter(
        user=user,
        viewed=False
    ).select_related('related_note', 'related_plan', 'related_step').order_by('-created_at')[:3]

    # Get time context
    time_context = NeuroFriendlyFeatures.get_time_context()

    # Get interface adaptations
    interface_prefs = NeuroFriendlyFeatures.adapt_interface({
        'prefers_minimal_motion': neuro_profile.prefers_minimal_motion,
        'prefers_high_contrast': neuro_profile.prefers_high_contrast,
        'prefers_larger_text': neuro_profile.prefers_larger_text,
        'quiet_mode': neuro_profile.quiet_mode,
    })

    context = {
        'neuro_profile': neuro_profile,
        'latest_mood': latest_mood,
        'recent_notes': recent_notes,
        'categories_with_counts': categories_with_counts,
        'active_plans': active_plans,
        'celebrations': celebrations,
        'time_context': time_context,
        'interface_prefs': interface_prefs,
    }

    return render(request, 'mindflow/dashboard.html', context)


@login_required
@require_http_methods(["GET", "POST"])
def capture_note(request):
    """Capture a brain dump note"""
    if request.method == 'POST':
        form = NoteForm(request.POST)
        if form.is_valid():
            note = form.save(commit=False)
            note.user = request.user
            note.status = 'captured'

            # Capture context
            if hasattr(request.user, 'mood_checkins'):
                latest_mood = request.user.mood_checkins.first()
                if latest_mood:
                    note.captured_at_energy = latest_mood.energy_level

            note.save()

            # Create celebration
            Celebration.objects.create(
                user=request.user,
                celebration_type='note_captured',
                message=NeuroFriendlyFeatures.generate_celebration_message('note_captured'),
                related_note=note
            )

            messages.success(request, "Your thoughts have been captured safely.")

            # If HTMX request, return partial
            if request.htmx:
                return redirect('mindflow:process_note', note_id=note.id)

            return redirect('mindflow:process_note', note_id=note.id)
    else:
        form = NoteForm()

    return render(request, 'mindflow/capture.html', {'form': form})


@login_required
@require_http_methods(["POST"])
def quick_capture(request):
    """Quick capture via HTMX"""
    content = request.POST.get('content', '').strip()

    if not content:
        return HttpResponse("Please enter some thoughts", status=400)

    note = Note.objects.create(
        user=request.user,
        content=content,
        status='captured'
    )

    # Capture energy context
    latest_mood = MoodCheckIn.objects.filter(user=request.user).first()
    if latest_mood:
        note.captured_at_energy = latest_mood.energy_level
        note.save(update_fields=['captured_at_energy'])

    if request.htmx:
        return render(request, 'mindflow/partials/note_card.html', {'note': note})

    return JsonResponse({'success': True, 'note_id': note.id})


@login_required
def process_note(request, note_id):
    """Process a note with AI"""
    note = get_object_or_404(Note, id=note_id, user=request.user)

    if note.status == 'captured':
        note.status = 'processing'
        note.save(update_fields=['status'])

        try:
            # Process with AI
            ai_processor = EmpathicAIProcessor()
            context = {
                'energy_level': note.captured_at_energy,
            }

            result = ai_processor.process_overwhelm(note.content, context)

            # Update note with AI results
            note.validation_message = result.get('validation', '')
            note.gentle_reframe = result.get('gentle_reframe', '')
            note.energy_impact = result.get('energy_impact', 'medium')
            note.actionable_items = result.get('actionable_items', [])
            note.processing_items = result.get('processing_items', [])
            note.tags = result.get('supportive_tags', [])
            note.is_actionable = len(result.get('actionable_items', [])) > 0

            # Get or create category
            category_name = result.get('category', 'mixed').title()
            category, _ = Category.objects.get_or_create(
                name=category_name,
                defaults={'is_system': True, 'slug': category_name.lower()}
            )
            note.category = category

            note.mark_processed()

            # Store embedding for semantic search
            try:
                ai_processor.store_note_embedding(
                    str(note.id),
                    note.content,
                    {'user_id': request.user.id, 'category': category_name}
                )
                note.embedding_id = str(note.id)
                note.save(update_fields=['embedding_id'])
            except Exception as e:
                logger.error(f"Error storing embedding: {e}")

            messages.success(request, "Your thoughts have been processed with care.")

        except Exception as e:
            logger.error(f"Error processing note: {e}")
            note.status = 'captured'
            note.save(update_fields=['status'])
            messages.error(request, "We had trouble processing that. Your note is still saved.")

    return render(request, 'mindflow/note_processed.html', {'note': note})


@login_required
def note_list(request):
    """List all notes - optimized with pagination"""
    notes_queryset = Note.objects.filter(
        user=request.user,
        status__in=['captured', 'processed', 'planned']
    ).select_related('category').order_by('-created_at')

    # Filter by category if provided
    category_slug = request.GET.get('category')
    if category_slug:
        notes_queryset = notes_queryset.filter(category__slug=category_slug)

    # Filter by tag if provided
    tag = request.GET.get('tag')
    if tag:
        notes_queryset = notes_queryset.filter(tags__contains=[tag])

    paginator = Paginator(notes_queryset, 20)
    page_number = request.GET.get('page')
    notes = paginator.get_page(page_number)

    return render(request, 'mindflow/note_list.html', {'notes': notes})


@login_required
def note_detail(request, note_id):
    """View a single note"""
    note = get_object_or_404(
        Note.objects.select_related('category'),
        id=note_id,
        user=request.user
    )
    return render(request, 'mindflow/note_detail.html', {'note': note})


@login_required
@require_http_methods(["POST"])
def archive_note(request, note_id):
    """Archive a note"""
    note = get_object_or_404(Note, id=note_id, user=request.user)
    note.archive()

    if request.htmx:
        return HttpResponse("Note archived", status=200)

    messages.success(request, "Note archived successfully.")
    return redirect('mindflow:note_list')


@login_required
@require_http_methods(["GET", "POST"])
def energy_checkin(request):
    """Energy/mood check-in"""
    if request.method == 'POST':
        form = EnergyCheckInForm(request.POST)
        if form.is_valid():
            checkin = form.save(commit=False)
            checkin.user = request.user
            checkin.save()

            # Create celebration
            Celebration.objects.create(
                user=request.user,
                celebration_type='energy_check',
                message=NeuroFriendlyFeatures.generate_celebration_message('energy_check')
            )

            # Get break suggestion based on energy
            break_suggestion = NeuroFriendlyFeatures.suggest_break_time(
                0,  # session duration
                checkin.energy_level
            )

            if request.htmx:
                return render(request, 'mindflow/partials/energy_feedback.html', {
                    'checkin': checkin,
                    'break_suggestion': break_suggestion
                })

            messages.success(request, "Thank you for checking in with yourself.")
            return redirect('mindflow:dashboard')
    else:
        form = EnergyCheckInForm()

    return render(request, 'mindflow/energy_checkin.html', {'form': form})


@login_required
def organize_category(request, category_slug):
    """View notes in a specific category"""
    category = get_object_or_404(Category, slug=category_slug)

    notes = Note.objects.filter(
        user=request.user,
        category=category,
        status__in=['captured', 'processed']
    ).order_by('-created_at')

    return render(request, 'mindflow/organize_category.html', {
        'category': category,
        'notes': notes
    })


@login_required
def plan_list(request):
    """List all plans - optimized"""
    plans = Plan.objects.filter(
        user=request.user
    ).prefetch_related(
        Prefetch('steps', queryset=Step.objects.order_by('order'))
    ).order_by('-updated_at')

    # Add completion percentages
    for plan in plans:
        plan.completion_percentage = plan.get_completion_percentage()

    return render(request, 'mindflow/plan_list.html', {'plans': plans})


@login_required
@require_http_methods(["GET", "POST"])
def create_plan(request):
    """Create a new plan from notes"""
    if request.method == 'POST':
        # Get selected notes
        note_ids = request.POST.getlist('notes')
        notes = Note.objects.filter(id__in=note_ids, user=request.user)

        if not notes:
            messages.error(request, "Please select at least one note.")
            return redirect('mindflow:create_plan')

        # Get user's neuro profile
        neuro_profile = NeuroProfile.objects.get(user=request.user)

        # Get current energy
        latest_mood = MoodCheckIn.objects.filter(user=request.user).first()
        energy_level = latest_mood.energy_level if latest_mood else 'medium'

        try:
            # Create plan with AI
            ai_processor = EmpathicAIProcessor()
            thoughts = [note.content for note in notes]

            plan_data = ai_processor.create_manageable_plan(
                thoughts,
                energy_level,
                {
                    'attention_span_preference': neuro_profile.attention_span_preference,
                    'needs_time_estimates': neuro_profile.needs_time_estimates,
                }
            )

            # Create plan
            plan = Plan.objects.create(
                user=request.user,
                title=plan_data.get('title', 'New Plan'),
                description=plan_data.get('description', ''),
                recommended_energy=plan_data.get('recommended_energy', 'medium'),
                status='active',
                started_at=timezone.now()
            )

            # Add source notes
            plan.source_notes.set(notes)

            # Create steps
            for i, step_data in enumerate(plan_data.get('steps', [])):
                Step.objects.create(
                    plan=plan,
                    order=i + 1,
                    title=step_data.get('title', f'Step {i+1}'),
                    description=step_data.get('description', ''),
                    micro_tasks=step_data.get('micro_tasks', []),
                    energy_cost=step_data.get('energy_cost', 'medium'),
                    estimated_minutes=step_data.get('estimated_minutes')
                )

            # Update progress
            plan.update_progress()

            # Mark notes as planned
            for note in notes:
                note.status = 'planned'
            Note.objects.bulk_update(notes, ['status'])

            # Create celebration
            Celebration.objects.create(
                user=request.user,
                celebration_type='plan_created',
                message=NeuroFriendlyFeatures.generate_celebration_message('plan_created'),
                related_plan=plan
            )

            messages.success(request, f"Created plan: {plan.title}")
            return redirect('mindflow:plan_detail', plan_id=plan.id)

        except Exception as e:
            logger.error(f"Error creating plan: {e}")
            messages.error(request, "Had trouble creating the plan. Please try again.")
            return redirect('mindflow:create_plan')

    else:
        # Show notes that can be turned into plans
        actionable_notes = Note.objects.filter(
            user=request.user,
            status='processed',
            is_actionable=True
        ).select_related('category').order_by('-created_at')[:20]

        return render(request, 'mindflow/create_plan.html', {
            'actionable_notes': actionable_notes
        })


@login_required
def plan_detail(request, plan_id):
    """View a plan with all steps - optimized"""
    plan = get_object_or_404(
        Plan.objects.prefetch_related(
            Prefetch('steps', queryset=Step.objects.order_by('order')),
            'source_notes'
        ),
        id=plan_id,
        user=request.user
    )

    plan.completion_percentage = plan.get_completion_percentage()
    plan.next_step_obj = plan.get_next_step()

    return render(request, 'mindflow/plan_detail.html', {'plan': plan})


@login_required
@require_http_methods(["POST"])
def complete_step(request, plan_id, step_id):
    """Mark a step as complete"""
    step = get_object_or_404(Step, id=step_id, plan_id=plan_id, plan__user=request.user)

    step.complete()

    # Create celebration
    Celebration.objects.create(
        user=request.user,
        celebration_type='step_completed',
        message=NeuroFriendlyFeatures.generate_celebration_message('step_completed'),
        related_step=step,
        related_plan=step.plan
    )

    # Check if plan is completed
    if step.plan.status == 'completed':
        Celebration.objects.create(
            user=request.user,
            celebration_type='plan_completed',
            message=NeuroFriendlyFeatures.generate_celebration_message('plan_completed'),
            related_plan=step.plan
        )

    if request.htmx:
        return render(request, 'mindflow/partials/step_card.html', {'step': step, 'plan': step.plan})

    messages.success(request, f"Completed: {step.title}")
    return redirect('mindflow:plan_detail', plan_id=plan_id)


@login_required
@require_http_methods(["POST"])
def start_step(request, plan_id, step_id):
    """Mark a step as started"""
    step = get_object_or_404(Step, id=step_id, plan_id=plan_id, plan__user=request.user)

    step.start()

    if request.htmx:
        return render(request, 'mindflow/partials/step_card.html', {'step': step, 'plan': step.plan})

    return redirect('mindflow:plan_detail', plan_id=plan_id)


@login_required
@require_http_methods(["GET", "POST"])
def neuro_profile_settings(request):
    """Manage neurodivergent profile settings"""
    profile, created = NeuroProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = NeuroProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Your preferences have been updated.")
            return redirect('mindflow:dashboard')
    else:
        form = NeuroProfileForm(instance=profile)

    return render(request, 'mindflow/neuro_profile_settings.html', {'form': form})


# HTMX Partials
@login_required
def partial_recent_notes(request):
    """HTMX partial for recent notes"""
    recent_notes = Note.objects.filter(
        user=request.user,
        status__in=['captured', 'processing', 'processed']
    ).select_related('category').order_by('-created_at')[:settings.MINDFLOW_RECENT_NOTES_COUNT]

    return render(request, 'mindflow/partials/recent_notes.html', {'recent_notes': recent_notes})


@login_required
def partial_thought_garden(request):
    """HTMX partial for thought garden"""
    categories_with_counts = Category.objects.filter(
        Q(user=request.user) | Q(is_system=True)
    ).annotate(
        note_count=Count('notes', filter=Q(notes__user=request.user, notes__status__in=['captured', 'processed']))
    ).filter(note_count__gt=0).order_by('-note_count')

    return render(request, 'mindflow/partials/thought_garden.html', {
        'categories_with_counts': categories_with_counts
    })


@login_required
def partial_active_plans(request):
    """HTMX partial for active plans"""
    active_plans = Plan.objects.filter(
        user=request.user,
        status='active'
    ).prefetch_related(
        Prefetch('steps', queryset=Step.objects.order_by('order'))
    ).order_by('-updated_at')[:settings.MINDFLOW_MAX_ACTIVE_PLANS]

    for plan in active_plans:
        plan.completion_percentage = plan.get_completion_percentage()
        plan.next_step_obj = plan.get_next_step()

    return render(request, 'mindflow/partials/active_plans.html', {'active_plans': active_plans})
