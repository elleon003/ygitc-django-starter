from django.db import models
from django.conf import settings
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator


class NeuroProfile(models.Model):
    """User's neurodivergent profile and preferences"""
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='neuro_profile')

    # Attention patterns
    ATTENTION_CHOICES = [
        ('short', '5-15 minutes'),
        ('medium', '15-30 minutes'),
        ('long', '30+ minutes'),
        ('variable', 'It depends on the day'),
    ]
    attention_span_preference = models.CharField(max_length=20, choices=ATTENTION_CHOICES, default='variable')

    # Sensory preferences
    prefers_minimal_motion = models.BooleanField(default=False, help_text="Reduce animations")
    prefers_high_contrast = models.BooleanField(default=False, help_text="Higher contrast colors")
    prefers_larger_text = models.BooleanField(default=False, help_text="Larger font sizes")
    quiet_mode = models.BooleanField(default=True, help_text="Disable sounds")

    # Executive function support
    needs_time_estimates = models.BooleanField(default=True)
    likes_step_breakdown = models.BooleanField(default=True)
    prefers_gentle_reminders = models.BooleanField(default=True)

    # Energy tracking
    tracks_energy_levels = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Neurodivergent Profile'
        verbose_name_plural = 'Neurodivergent Profiles'

    def __str__(self):
        return f"{self.user.email}'s Neuro Profile"

    def get_session_length(self):
        """Get recommended session length in minutes"""
        session_map = {
            'short': 10,
            'medium': 20,
            'long': 30,
            'variable': 15,
        }
        return session_map.get(self.attention_span_preference, 15)


class MoodCheckIn(models.Model):
    """Track user's energy and mental state"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='mood_checkins')

    ENERGY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    ]
    energy_level = models.CharField(max_length=10, choices=ENERGY_CHOICES)

    overwhelm_level = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        help_text="1-10 scale"
    )

    FOCUS_CHOICES = [
        ('scattered', 'Scattered'),
        ('focused', 'Focused'),
        ('hyperfocus', 'Hyperfocused'),
        ('foggy', 'Brain fog'),
    ]
    focus_quality = models.CharField(max_length=20, choices=FOCUS_CHOICES)

    notes = models.TextField(blank=True, help_text="Optional notes about how you're feeling")

    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Mood Check-In'
        verbose_name_plural = 'Mood Check-Ins'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['user', '-timestamp']),
        ]

    def __str__(self):
        return f"{self.user.email} - {self.energy_level} energy ({self.timestamp.strftime('%Y-%m-%d %H:%M')})"


class Category(models.Model):
    """Categories for organizing thoughts"""
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    color = models.CharField(max_length=7, default='#d4a574', help_text="Hex color code")
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, blank=True, help_text="Lucide icon name")

    # System vs user created
    is_system = models.BooleanField(default=False, help_text="System-generated category")
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='custom_categories'
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'
        ordering = ['name']
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['user', 'is_system']),
        ]

    def __str__(self):
        return self.name


class Note(models.Model):
    """Brain dump notes with AI processing"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notes')

    # Core content
    content = models.TextField(help_text="The raw brain dump")
    processed_content = models.TextField(blank=True, help_text="AI-processed/cleaned content")

    # AI analysis results
    validation_message = models.TextField(blank=True, help_text="Empathic validation from AI")
    gentle_reframe = models.TextField(blank=True, help_text="Kinder perspective on thoughts")

    # Categorization
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name='notes')
    tags = models.JSONField(default=list, help_text="Supportive tags for organization")

    # Energy and actionability
    ENERGY_IMPACT_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    ]
    energy_impact = models.CharField(max_length=10, choices=ENERGY_IMPACT_CHOICES, blank=True)

    is_actionable = models.BooleanField(default=False)
    actionable_items = models.JSONField(default=list, help_text="Extracted action items")
    processing_items = models.JSONField(default=list, help_text="Things to think about")

    # Context
    captured_at_energy = models.CharField(max_length=10, choices=MoodCheckIn.ENERGY_CHOICES, blank=True)
    location_context = models.CharField(max_length=200, blank=True)
    time_context = models.CharField(max_length=100, blank=True)

    # Status
    STATUS_CHOICES = [
        ('captured', 'Captured'),
        ('processing', 'Processing'),
        ('processed', 'Processed'),
        ('planned', 'Planned'),
        ('archived', 'Archived'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='captured')

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    processed_at = models.DateTimeField(null=True, blank=True)
    archived_at = models.DateTimeField(null=True, blank=True)

    # Vector embedding for semantic search
    embedding_id = models.CharField(max_length=255, blank=True, help_text="ChromaDB embedding ID")

    class Meta:
        verbose_name = 'Note'
        verbose_name_plural = 'Notes'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['user', 'status']),
            models.Index(fields=['category']),
        ]

    def __str__(self):
        return f"{self.user.email} - {self.content[:50]}..."

    def mark_processed(self):
        """Mark note as processed"""
        self.status = 'processed'
        self.processed_at = timezone.now()
        self.save(update_fields=['status', 'processed_at'])

    def archive(self):
        """Archive the note"""
        self.status = 'archived'
        self.archived_at = timezone.now()
        self.save(update_fields=['status', 'archived_at'])


class Plan(models.Model):
    """Action plans created from notes"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='plans')

    # Core plan info
    title = models.CharField(max_length=255, help_text="Encouraging plan title")
    description = models.TextField(blank=True)

    # Source notes
    source_notes = models.ManyToManyField(Note, related_name='plans', blank=True)

    # Energy considerations
    recommended_energy = models.CharField(
        max_length=10,
        choices=MoodCheckIn.ENERGY_CHOICES,
        help_text="Recommended energy level to work on this"
    )

    # Status
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('paused', 'Paused'),
        ('completed', 'Completed'),
        ('archived', 'Archived'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')

    # Progress tracking
    total_steps = models.IntegerField(default=0)
    completed_steps = models.IntegerField(default=0)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = 'Plan'
        verbose_name_plural = 'Plans'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['user', '-created_at']),
        ]

    def __str__(self):
        return f"{self.title} ({self.status})"

    def get_completion_percentage(self):
        """Calculate completion percentage"""
        if self.total_steps == 0:
            return 0
        return int((self.completed_steps / self.total_steps) * 100)

    def get_next_step(self):
        """Get the next incomplete step"""
        return self.steps.filter(status='pending').order_by('order').first()

    def update_progress(self):
        """Update progress counters"""
        self.total_steps = self.steps.count()
        self.completed_steps = self.steps.filter(status='completed').count()

        if self.total_steps > 0 and self.completed_steps == self.total_steps:
            self.status = 'completed'
            self.completed_at = timezone.now()

        self.save(update_fields=['total_steps', 'completed_steps', 'status', 'completed_at'])


class Step(models.Model):
    """Individual steps within a plan"""
    plan = models.ForeignKey(Plan, on_delete=models.CASCADE, related_name='steps')

    # Step details
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    order = models.IntegerField(default=0)

    # Micro-tasks
    micro_tasks = models.JSONField(default=list, help_text="Tiny actionable tasks")

    # Energy cost
    ENERGY_COST_CHOICES = [
        ('low', 'Low energy needed'),
        ('medium', 'Medium energy needed'),
        ('high', 'High energy needed'),
    ]
    energy_cost = models.CharField(max_length=10, choices=ENERGY_COST_CHOICES, default='medium')

    # Time estimate
    estimated_minutes = models.IntegerField(null=True, blank=True, help_text="Estimated time in minutes")

    # Status
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('skipped', 'Skipped'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = 'Step'
        verbose_name_plural = 'Steps'
        ordering = ['plan', 'order']
        indexes = [
            models.Index(fields=['plan', 'order']),
            models.Index(fields=['plan', 'status']),
        ]

    def __str__(self):
        return f"{self.plan.title} - Step {self.order}: {self.title}"

    def complete(self):
        """Mark step as completed and update plan progress"""
        self.status = 'completed'
        self.completed_at = timezone.now()
        self.save(update_fields=['status', 'completed_at'])

        # Update parent plan
        self.plan.update_progress()

    def start(self):
        """Mark step as in progress"""
        if self.status == 'pending':
            self.status = 'in_progress'
            self.started_at = timezone.now()
            self.save(update_fields=['status', 'started_at'])


class Celebration(models.Model):
    """Track celebrations and achievements"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='celebrations')

    # What was celebrated
    CELEBRATION_TYPE_CHOICES = [
        ('note_captured', 'Captured a thought'),
        ('plan_created', 'Created a plan'),
        ('step_completed', 'Completed a step'),
        ('plan_completed', 'Completed a plan'),
        ('streak', 'Maintained a streak'),
        ('energy_check', 'Checked in with energy'),
    ]
    celebration_type = models.CharField(max_length=30, choices=CELEBRATION_TYPE_CHOICES)

    message = models.CharField(max_length=255, help_text="Encouraging message")

    # Related objects
    related_note = models.ForeignKey(Note, on_delete=models.SET_NULL, null=True, blank=True)
    related_plan = models.ForeignKey(Plan, on_delete=models.SET_NULL, null=True, blank=True)
    related_step = models.ForeignKey(Step, on_delete=models.SET_NULL, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    viewed = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Celebration'
        verbose_name_plural = 'Celebrations'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['user', 'viewed']),
        ]

    def __str__(self):
        return f"{self.user.email} - {self.celebration_type}"
