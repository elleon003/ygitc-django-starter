# AI Prompt: Build "MindFlow" - Neurodivergent-Friendly Brain Dump & Action Planning App

## 🎯 Project Overview

**App Name:** MindFlow  
**Tagline:** "Transform overwhelm into action"  
**Target User:** Neurodivergent individuals who experience thought overwhelm and need structured ways to process and organize their mental load

## 🎨 Brand Identity & Design Philosophy

### Visual Identity
- **Primary Question Prompt:** "What feels overwhelming right now?"
- **Brand Personality:** Calming, supportive, non-judgmental, empowering
- **Design Approach:** Clean minimalism with gentle curves, plenty of white space, and intuitive flow

### Color Palette & Psychology
```css
/* Primary Colors */
$rebecca-purple: #6b3fa0ff;   /* Trust, wisdom, creativity - primary actions */
$sandy-clay: #d4a574ff;       /* Warmth, comfort, grounding - secondary elements */
$light-sea-green: #20b2aaff;  /* Calm, healing, progress - success states */
$bright-snow: #f8f7f4ff;      /* Clean, spacious, peaceful - backgrounds */
$shadow-grey: #140c1dff;      /* Focus, depth, text - typography */
```

**Color Usage Strategy:**
- **Rebecca Purple (#6b3fa0):** Primary buttons, progress indicators, active states
- **Sandy Clay (#d4a574):** Warm accents, category tags, gentle highlights
- **Light Sea Green (#20b2aa):** Completion states, positive feedback, calm actions
- **Bright Snow (#f8f7f4):** Main backgrounds, card backgrounds, breathing space
- **Shadow Grey (#140c1d):** Primary text, important information, focus elements

### Typography & Accessibility
- **Primary Font:** Inter or Source Sans Pro (clean, readable, neurodivergent-friendly)
- **Font Sizes:** Generous line spacing, clear hierarchy
- **Contrast:** WCAG AAA compliance for all text
- **Reading Flow:** Left-aligned text, short paragraphs, clear sections

## 🧠 User Experience Design for Neurodivergent Minds

### Core UX Principles
1. **Low Cognitive Load:** One primary action per screen
2. **Predictable Patterns:** Consistent layouts and interactions
3. **Gentle Guidance:** Soft prompts instead of demanding commands
4. **Progress Visibility:** Clear indicators of what's been accomplished
5. **Escape Routes:** Easy ways to pause, save, or start over
6. **Sensory Consideration:** No flashing, gentle animations, optional sounds

### Information Architecture
```
Dashboard (Home)
├── Quick Capture Zone
├── Recent Thoughts (last 5)
├── Active Plans (2-3 max visible)
├── Gentle Insights ("You've captured X thoughts this week")
└── Progress Celebrations

Capture Flow
├── "What feels overwhelming?" (large, calm text input)
├── Optional context ("Where are you?" "What time is it?")
├── AI Processing (with calming loader)
└── Gentle categorization results

Organize & Plan
├── Thought Garden (visual organization of notes)
├── Plan Creator (step-by-step wizard)
├── Plan Evolution (add to existing plans)
└── Archive (completed items)
```

## 🏗️ Technical Implementation Plan

### Tech Stack
```yaml
Backend:
  Framework: Django + Django Ninja
  Database: PostgreSQL + ChromaDB (vector storage)
  AI: Ollama (Llama3:8b + nomic-embed-text)
  Authentication: Django Auth + Social Auth

Frontend:
  Framework: Django Templates + HTMX + Alpine.js
  Styling: Tailwind CSS (custom design system)
  Icons: Lucide Icons (gentle, rounded style)
  Animations: CSS transitions + Framer Motion principles

Deployment:
  Platform: Railway or Render
  Storage: AWS S3 for file uploads
  Monitoring: Sentry for error tracking
  Analytics: Privacy-focused (PostHog or Plausible)
```

### Core Features & Implementation

#### 1. Gentle Capture Interface
```html
<!-- Main capture card -->
<div class="capture-card">
  <h2 class="gentle-prompt">What feels overwhelming right now?</h2>
  <textarea 
    class="overflow-input"
    placeholder="Let it all out... there's no wrong way to do this"
    rows="6">
  </textarea>
  <div class="comfort-actions">
    <button class="primary-btn">I'm ready to process this</button>
    <button class="gentle-btn">Save for later</button>
  </div>
</div>

<style>
.capture-card {
  background: var(--bright-snow);
  border: 2px solid var(--light-sea-green);
  border-radius: 16px;
  padding: 2rem;
  box-shadow: 0 8px 32px rgba(107, 63, 160, 0.1);
}

.gentle-prompt {
  color: var(--shadow-grey);
  font-size: 1.5rem;
  font-weight: 400;
  margin-bottom: 1.5rem;
  line-height: 1.4;
}

.overflow-input {
  width: 100%;
  border: 2px solid var(--sandy-clay);
  border-radius: 12px;
  padding: 1rem;
  font-size: 1.1rem;
  line-height: 1.6;
  background: var(--bright-snow);
  resize: vertical;
  min-height: 120px;
}
</style>
```

#### 2. AI Processing with Empathy
```python
class EmpathicAIProcessor:
    def process_overwhelm(self, content: str, context: dict = None) -> dict:
        """Process brain dump with neurodivergent-friendly approach"""
        
        prompt = f"""
        You are a gentle, understanding AI assistant helping someone who feels overwhelmed. 
        They've shared these thoughts: "{content}"
        
        Please analyze with empathy and provide:
        
        1. Validation (acknowledge their feelings)
        2. Gentle categorization (what type of thoughts are these?)
        3. Energy level assessment (how much mental energy is this taking?)
        4. Actionability (what could be acted on vs. what needs processing)
        5. Supportive tags (helpful for later organization)
        6. A kind reframe of their thoughts
        
        Remember: This person may have ADHD, autism, anxiety, or other neurodivergent traits.
        Be supportive, non-judgmental, and practical.
        
        Respond in this caring JSON format:
        {{
            "validation": "gentle acknowledgment of their experience",
            "category": "thoughts|feelings|tasks|worries|ideas",
            "energy_impact": "low|medium|high",
            "actionable_items": ["specific things they could do"],
            "processing_items": ["things to think about or feel"],
            "supportive_tags": ["helpful", "organizing", "tags"],
            "gentle_reframe": "a kinder way to see these thoughts",
            "next_steps": "suggested next action"
        }}
        """
        
        # Process with local AI model
        response = self.llm_client.generate(model='llama3:8b', prompt=prompt)
        return self.parse_empathic_response(response)
    
    def create_manageable_plan(self, thoughts: list, energy_level: str) -> dict:
        """Create plans that respect neurodivergent energy patterns"""
        
        prompt = f"""
        Help create a manageable action plan for someone who feels overwhelmed.
        Their energy level is: {energy_level}
        Their thoughts: {thoughts}
        
        Create a plan that:
        - Breaks things into tiny, manageable steps
        - Considers executive function challenges
        - Includes rest and reward
        - Has flexibility built in
        - Feels achievable, not overwhelming
        
        Include:
        - A encouraging title
        - Maximum 5 main steps
        - Each step broken into micro-tasks
        - Estimated energy cost (low/medium/high)
        - Built-in breaks
        - Celebration moments
        
        Format as supportive JSON...
        """
        
        return self.process_plan_creation(prompt)
```

#### 3. Calming Dashboard Design
```html
<!-- Dashboard Layout -->
<div class="mindflow-dashboard">
  <!-- Header with gentle greeting -->
  <header class="gentle-header">
    <div class="greeting">
      <h1>Hello, {{ user.first_name }}</h1>
      <p class="time-awareness">{{ current_time_context }}</p>
    </div>
    <div class="energy-check">
      <span>Energy level?</span>
      <div class="energy-buttons">
        <button class="energy-low">🌙 Low</button>
        <button class="energy-medium">🌤️ Medium</button>
        <button class="energy-high">☀️ High</button>
      </div>
    </div>
  </header>

  <!-- Quick capture always available -->
  <section class="quick-capture">
    <div class="capture-prompt">
      <h2>What feels overwhelming right now?</h2>
      <textarea hx-post="/capture/quick" hx-trigger="keyup delay:2s"></textarea>
    </div>
  </section>

  <!-- Gentle progress indicators -->
  <section class="progress-garden">
    <h3>Your Thought Garden</h3>
    <div class="thought-clusters">
      {% for category, notes in organized_notes.items %}
        <div class="thought-cluster" style="--cluster-color: {{ category.color }}">
          <h4>{{ category.name }}</h4>
          <div class="note-count">{{ notes|length }} thoughts</div>
          <div class="cluster-actions">
            <button hx-get="/organize/{{ category.slug }}">Tend to these</button>
          </div>
        </div>
      {% endfor %}
    </div>
  </section>

  <!-- Active plans (limited to prevent overwhelm) -->
  <section class="active-plans">
    <h3>What you're working on</h3>
    {% for plan in active_plans|slice:":3" %}
      <div class="plan-card">
        <h4>{{ plan.title }}</h4>
        <div class="progress-bar">
          <div class="progress" style="width: {{ plan.completion_percentage }}%"></div>
        </div>
        <div class="next-step">
          Next: {{ plan.next_step.title }}
        </div>
      </div>
    {% endfor %}
  </section>
</div>

<style>
.mindflow-dashboard {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
  background: var(--bright-snow);
}

.gentle-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
  padding-bottom: 1rem;
  border-bottom: 2px solid var(--light-sea-green);
}

.greeting h1 {
  color: var(--shadow-grey);
  font-weight: 300;
  font-size: 2rem;
  margin-bottom: 0.5rem;
}

.thought-cluster {
  background: linear-gradient(135deg, var(--bright-snow) 0%, rgba(212, 165, 116, 0.1) 100%);
  border: 2px solid var(--cluster-color, var(--sandy-clay));
  border-radius: 16px;
  padding: 1.5rem;
  margin: 1rem;
  transition: transform 0.2s ease;
}

.thought-cluster:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 24px rgba(107, 63, 160, 0.15);
}

.plan-card {
  background: var(--bright-snow);
  border-left: 4px solid var(--rebecca-purple);
  border-radius: 0 12px 12px 0;
  padding: 1.5rem;
  margin: 1rem 0;
}

.progress-bar {
  background: rgba(107, 63, 160, 0.1);
  height: 8px;
  border-radius: 4px;
  overflow: hidden;
  margin: 1rem 0;
}

.progress {
  background: linear-gradient(90deg, var(--rebecca-purple) 0%, var(--light-sea-green) 100%);
  height: 100%;
  transition: width 0.3s ease;
}
</style>
```

#### 4. Neurodivergent-Friendly Features

```python
# Specialized features for neurodivergent users
class NeuroFriendlyFeatures:
    
    def suggest_break_time(self, session_duration: int, energy_level: str) -> dict:
        """Suggest breaks based on neurodivergent attention patterns"""
        break_suggestions = {
            'high': 25,  # Pomodoro-style
            'medium': 15,  # Shorter bursts
            'low': 10   # Very gentle approach
        }
        
        return {
            'suggested_break_time': break_suggestions.get(energy_level, 15),
            'break_activities': [
                'Deep breathing for 2 minutes',
                'Stretch your arms and neck',
                'Drink some water',
                'Look at something far away'
            ]
        }
    
    def adapt_interface(self, user_preferences: dict) -> dict:
        """Adapt interface based on sensory preferences"""
        return {
            'reduce_motion': user_preferences.get('motion_sensitive', False),
            'high_contrast': user_preferences.get('high_contrast', False),
            'larger_text': user_preferences.get('larger_text', False),
            'quiet_mode': user_preferences.get('quiet_mode', False)
        }
    
    def executive_function_support(self, task_complexity: str) -> dict:
        """Provide executive function scaffolding"""
        if task_complexity == 'high':
            return {
                'break_down_further': True,
                'add_time_estimates': True,
                'suggest_body_doubling': True,
                'include_prep_steps': True
            }
        return {'gentle_reminders': True}
```

#### 5. Data Models for Neurodivergent Needs

```python
# Enhanced models for neurodivergent support
class NeuroProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    
    # Attention patterns
    attention_span_preference = models.CharField(max_length=20, choices=[
        ('short', '5-15 minutes'),
        ('medium', '15-30 minutes'),
        ('long', '30+ minutes'),
        ('variable', 'It depends on the day')
    ], default='variable')
    
    # Sensory preferences
    prefers_minimal_motion = models.BooleanField(default=False)
    prefers_high_contrast = models.BooleanField(default=False)
    prefers_larger_text = models.BooleanField(default=False)
    
    # Executive function support
    needs_time_estimates = models.BooleanField(default=True)
    likes_step_breakdown = models.BooleanField(default=True)
    prefers_gentle_reminders = models.BooleanField(default=True)
    
    # Energy tracking
    tracks_energy_levels = models.BooleanField(default=True)
    
    def get_personalized_settings(self):
        return {
            'session_length': self.get_session_length(),
            'interface_adaptations': self.get_interface_adaptations(),
            'support_level': self.get_support_level()
        }

class MoodCheckIn(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    energy_level = models.CharField(max_length=10, choices=[
        ('low', 'Low'),
        ('medium', 'Medium'), 
        ('high', 'High')
    ])
    overwhelm_level = models.IntegerField(choices=[(i, i) for i in range(1, 11)])
    focus_quality = models.CharField(max_length=20, choices=[
        ('scattered', 'Scattered'),
        ('focused', 'Focused'),
        ('hyperfocus', 'Hyperfocused'),
        ('foggy', 'Brain fog')
    ])
    timestamp = models.DateTimeField(auto_now_add=True)
```

## 🎯 Unique Value Propositions

### For ADHD Users
- **Dopamine-friendly:** Quick wins, progress visualization, gentle gamification
- **Attention-aware:** Adaptive session lengths, break reminders
- **Hyperfocus support:** Save states, gentle interruption systems

### For Autistic Users
- **Predictable patterns:** Consistent layouts, clear expectations
- **Sensory considerations:** Customizable visual settings, calm color palette
- **Detail orientation:** Thorough organization, comprehensive planning

### For Anxiety-Prone Users
- **Non-judgmental:** Gentle language, no pressure
- **Control:** Clear escape routes, save-for-later options
- **Validation:** AI responses acknowledge feelings

### For Executive Function Challenges
- **Scaffolding:** Step-by-step breakdowns, time estimates
- **Memory support:** Visual reminders, progress tracking
- **Initiation help:** "Next tiny step" guidance

## 📱 Implementation Timeline

### Week 1: Foundation
- Django setup with custom design system
- Basic note capture and AI processing
- User authentication and profiles

### Week 2: Core Features
- Action plan generation
- Knowledge synthesis
- Responsive neurodivergent-friendly UI

### Week 3: Polish & Deploy
- Accessibility auditing
- Performance optimization
- User testing with neurodivergent beta users
- Railway deployment

## 🎨 Brand Assets & Messaging

### Logo Concept
- Gentle brain silhouette with flowing thought streams
- Uses rebecca purple and light sea green
- Rounded, organic shapes (never harsh angles)

### Voice & Tone
- **Supportive:** "You're doing great"
- **Non-judgmental:** "There's no wrong way to think"
- **Empowering:** "Let's turn this into action"
- **Gentle:** "Take your time"
- **Understanding:** "I get it"

### Sample Copy
```
Welcome Message: "Welcome to your safe space for overwhelming thoughts"
Empty State: "Nothing here yet, and that's perfectly okay"
Error Message: "Oops, something got tangled. Let's try again gently"
Success: "Beautiful work! You're building something meaningful"
```

This prompt provides a comprehensive blueprint for building MindFlow - a genuinely neurodivergent-friendly brain dump and action planning application that transforms the overwhelming question "What feels overwhelming right now?" into structured, manageable action through empathetic AI and thoughtful design.