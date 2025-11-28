from django import forms
from .models import Note, MoodCheckIn, NeuroProfile, Plan


class NoteForm(forms.ModelForm):
    """Form for capturing brain dump notes"""

    class Meta:
        model = Note
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'overflow-input w-full border-2 border-sandy-clay rounded-xl p-4 text-lg leading-relaxed bg-bright-snow resize-y min-h-[120px] focus:ring-2 focus:ring-rebecca-purple focus:border-rebecca-purple transition-all',
                'placeholder': 'Let it all out... there\'s no wrong way to do this',
                'rows': 6,
            })
        }
        labels = {
            'content': ''
        }


class EnergyCheckInForm(forms.ModelForm):
    """Form for energy/mood check-ins"""

    class Meta:
        model = MoodCheckIn
        fields = ['energy_level', 'overwhelm_level', 'focus_quality', 'notes']
        widgets = {
            'energy_level': forms.RadioSelect(attrs={
                'class': 'energy-radio'
            }),
            'overwhelm_level': forms.Select(attrs={
                'class': 'form-select rounded-lg border-sandy-clay focus:ring-rebecca-purple focus:border-rebecca-purple'
            }),
            'focus_quality': forms.RadioSelect(attrs={
                'class': 'focus-radio'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'w-full border-2 border-sandy-clay rounded-lg p-3 text-base bg-bright-snow resize-y',
                'placeholder': 'Optional: How are you feeling right now?',
                'rows': 3,
            })
        }
        labels = {
            'energy_level': 'What\'s your energy level right now?',
            'overwhelm_level': 'How overwhelmed do you feel? (1-10)',
            'focus_quality': 'How\'s your focus?',
            'notes': 'Anything else you want to share?'
        }


class NeuroProfileForm(forms.ModelForm):
    """Form for neurodivergent profile settings"""

    class Meta:
        model = NeuroProfile
        fields = [
            'attention_span_preference',
            'prefers_minimal_motion',
            'prefers_high_contrast',
            'prefers_larger_text',
            'quiet_mode',
            'needs_time_estimates',
            'likes_step_breakdown',
            'prefers_gentle_reminders',
            'tracks_energy_levels',
        ]
        widgets = {
            'attention_span_preference': forms.RadioSelect(),
            'prefers_minimal_motion': forms.CheckboxInput(attrs={
                'class': 'rounded border-sandy-clay text-rebecca-purple focus:ring-rebecca-purple'
            }),
            'prefers_high_contrast': forms.CheckboxInput(attrs={
                'class': 'rounded border-sandy-clay text-rebecca-purple focus:ring-rebecca-purple'
            }),
            'prefers_larger_text': forms.CheckboxInput(attrs={
                'class': 'rounded border-sandy-clay text-rebecca-purple focus:ring-rebecca-purple'
            }),
            'quiet_mode': forms.CheckboxInput(attrs={
                'class': 'rounded border-sandy-clay text-rebecca-purple focus:ring-rebecca-purple'
            }),
            'needs_time_estimates': forms.CheckboxInput(attrs={
                'class': 'rounded border-sandy-clay text-rebecca-purple focus:ring-rebecca-purple'
            }),
            'likes_step_breakdown': forms.CheckboxInput(attrs={
                'class': 'rounded border-sandy-clay text-rebecca-purple focus:ring-rebecca-purple'
            }),
            'prefers_gentle_reminders': forms.CheckboxInput(attrs={
                'class': 'rounded border-sandy-clay text-rebecca-purple focus:ring-rebecca-purple'
            }),
            'tracks_energy_levels': forms.CheckboxInput(attrs={
                'class': 'rounded border-sandy-clay text-rebecca-purple focus:ring-rebecca-purple'
            }),
        }
        labels = {
            'attention_span_preference': 'How long can you typically focus?',
            'prefers_minimal_motion': 'Reduce animations and motion',
            'prefers_high_contrast': 'Use higher contrast colors',
            'prefers_larger_text': 'Use larger text sizes',
            'quiet_mode': 'Disable sounds and notifications',
            'needs_time_estimates': 'Show time estimates for tasks',
            'likes_step_breakdown': 'Break tasks into smaller steps',
            'prefers_gentle_reminders': 'Receive gentle reminders',
            'tracks_energy_levels': 'Track your energy levels',
        }
        help_texts = {
            'attention_span_preference': 'This helps us suggest appropriate break times',
            'prefers_minimal_motion': 'Helpful for motion sensitivity',
            'prefers_high_contrast': 'Easier to read for some people',
            'prefers_larger_text': 'More comfortable for reading',
        }


class PlanForm(forms.ModelForm):
    """Form for manually creating plans"""

    class Meta:
        model = Plan
        fields = ['title', 'description', 'recommended_energy']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'w-full border-2 border-sandy-clay rounded-lg p-3 text-lg bg-bright-snow focus:ring-rebecca-purple focus:border-rebecca-purple',
                'placeholder': 'Give your plan an encouraging title',
            }),
            'description': forms.Textarea(attrs={
                'class': 'w-full border-2 border-sandy-clay rounded-lg p-3 text-base bg-bright-snow resize-y',
                'placeholder': 'What does this plan help you accomplish?',
                'rows': 4,
            }),
            'recommended_energy': forms.RadioSelect(),
        }
        labels = {
            'title': 'Plan Title',
            'description': 'Description',
            'recommended_energy': 'What energy level works best for this?',
        }
