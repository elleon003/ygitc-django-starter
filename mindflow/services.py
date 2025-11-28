import json
import logging
from typing import Dict, List, Optional
from django.conf import settings
import ollama
import chromadb
from chromadb.config import Settings as ChromaSettings

logger = logging.getLogger(__name__)


class EmpathicAIProcessor:
    """AI processor with neurodivergent-friendly empathic responses"""

    def __init__(self):
        self.client = ollama.Client(host=settings.OLLAMA_BASE_URL)
        self.model = settings.OLLAMA_MODEL
        self.embed_model = settings.OLLAMA_EMBED_MODEL

        # Initialize ChromaDB
        self.chroma_client = chromadb.PersistentClient(
            path=settings.CHROMADB_PATH,
            settings=ChromaSettings(anonymized_telemetry=False)
        )
        self.collection = self.chroma_client.get_or_create_collection(
            name=settings.CHROMADB_COLLECTION_NAME,
            metadata={"description": "MindFlow thought embeddings"}
        )

    def process_overwhelm(self, content: str, context: Optional[Dict] = None) -> Dict:
        """
        Process brain dump with neurodivergent-friendly approach

        Args:
            content: The raw brain dump text
            context: Optional context (energy_level, location, time, etc.)

        Returns:
            Dict with empathic analysis results
        """
        context = context or {}

        prompt = f"""You are a gentle, understanding AI assistant helping someone who feels overwhelmed.
They've shared these thoughts: "{content}"

{f"Context: Energy level is {context.get('energy_level', 'unknown')}" if context.get('energy_level') else ""}

Please analyze with empathy and provide:

1. **Validation** - Acknowledge their feelings warmly (2-3 sentences)
2. **Category** - What type of thoughts are these? (Choose ONE: thoughts, feelings, tasks, worries, ideas, mixed)
3. **Energy Impact** - How much mental energy is this taking? (low, medium, high)
4. **Actionable Items** - Specific things they could do (list 0-5 items)
5. **Processing Items** - Things to think about or feel (list 0-5 items)
6. **Supportive Tags** - Helpful organizing tags (3-7 tags)
7. **Gentle Reframe** - A kinder way to see these thoughts (2-3 sentences)
8. **Next Steps** - ONE suggested next action

Remember: This person may have ADHD, autism, anxiety, or other neurodivergent traits.
Be supportive, non-judgmental, and practical.

Respond ONLY with valid JSON in this exact format (no markdown, no code blocks):
{{
    "validation": "gentle acknowledgment of their experience",
    "category": "thoughts",
    "energy_impact": "medium",
    "actionable_items": ["specific action 1", "specific action 2"],
    "processing_items": ["feeling to process", "thought to explore"],
    "supportive_tags": ["tag1", "tag2", "tag3"],
    "gentle_reframe": "a kinder perspective",
    "next_steps": "one clear next action"
}}"""

        try:
            response = self.client.generate(
                model=self.model,
                prompt=prompt,
                options={
                    'temperature': 0.7,
                    'top_p': 0.9,
                }
            )

            result = self._parse_json_response(response['response'])
            return result

        except Exception as e:
            logger.error(f"Error processing overwhelm: {e}")
            return self._fallback_response()

    def create_manageable_plan(
        self,
        thoughts: List[str],
        energy_level: str,
        user_preferences: Optional[Dict] = None
    ) -> Dict:
        """
        Create plans that respect neurodivergent energy patterns

        Args:
            thoughts: List of thought contents to plan from
            energy_level: Current energy level (low, medium, high)
            user_preferences: Optional user preferences

        Returns:
            Dict with plan structure
        """
        user_preferences = user_preferences or {}
        thoughts_text = "\n- ".join(thoughts)

        prompt = f"""Help create a manageable action plan for someone who feels overwhelmed.

Their energy level is: {energy_level}
Their thoughts:
- {thoughts_text}

{f"Preferences: {user_preferences.get('attention_span_preference', 'variable')} attention span" if user_preferences.get('attention_span_preference') else ""}

Create a plan that:
- Breaks things into tiny, manageable steps
- Considers executive function challenges
- Includes rest and rewards
- Has flexibility built in
- Feels achievable, not overwhelming

Provide:
1. An **encouraging title** (4-8 words)
2. A brief **description** (1-2 sentences)
3. **Maximum 5 main steps**, each with:
   - Clear title
   - Simple description
   - 2-4 micro-tasks (very specific, tiny actions)
   - Energy cost (low, medium, high)
   - Time estimate in minutes
4. **Recommended energy level** to work on this (low, medium, high)

Respond ONLY with valid JSON (no markdown, no code blocks):
{{
    "title": "Encouraging Plan Title",
    "description": "Brief supportive description",
    "recommended_energy": "medium",
    "steps": [
        {{
            "title": "Step title",
            "description": "What this step involves",
            "micro_tasks": ["tiny task 1", "tiny task 2"],
            "energy_cost": "low",
            "estimated_minutes": 10
        }}
    ]
}}"""

        try:
            response = self.client.generate(
                model=self.model,
                prompt=prompt,
                options={
                    'temperature': 0.7,
                    'top_p': 0.9,
                }
            )

            result = self._parse_json_response(response['response'])
            return result

        except Exception as e:
            logger.error(f"Error creating plan: {e}")
            return self._fallback_plan()

    def generate_embedding(self, text: str) -> List[float]:
        """Generate vector embedding for semantic search"""
        try:
            response = self.client.embeddings(
                model=self.embed_model,
                prompt=text
            )
            return response['embedding']
        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            return []

    def store_note_embedding(self, note_id: str, content: str, metadata: Dict):
        """Store note embedding in ChromaDB"""
        try:
            embedding = self.generate_embedding(content)
            if embedding:
                self.collection.add(
                    ids=[note_id],
                    embeddings=[embedding],
                    documents=[content],
                    metadatas=[metadata]
                )
        except Exception as e:
            logger.error(f"Error storing embedding: {e}")

    def find_similar_notes(self, query: str, user_id: int, n_results: int = 5) -> List[Dict]:
        """Find semantically similar notes"""
        try:
            query_embedding = self.generate_embedding(query)
            if not query_embedding:
                return []

            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results,
                where={"user_id": user_id}
            )

            similar_notes = []
            if results and results['ids']:
                for i, note_id in enumerate(results['ids'][0]):
                    similar_notes.append({
                        'note_id': note_id,
                        'content': results['documents'][0][i],
                        'distance': results['distances'][0][i] if 'distances' in results else None,
                        'metadata': results['metadatas'][0][i] if 'metadatas' in results else {}
                    })

            return similar_notes

        except Exception as e:
            logger.error(f"Error finding similar notes: {e}")
            return []

    def _parse_json_response(self, response: str) -> Dict:
        """Parse JSON from AI response, handling common issues"""
        try:
            # Remove markdown code blocks if present
            response = response.strip()
            if response.startswith('```'):
                lines = response.split('\n')
                response = '\n'.join(lines[1:-1]) if len(lines) > 2 else response
                response = response.replace('```json', '').replace('```', '').strip()

            return json.loads(response)
        except json.JSONDecodeError as e:
            logger.error(f"JSON parse error: {e}, Response: {response}")
            raise

    def _fallback_response(self) -> Dict:
        """Fallback response if AI processing fails"""
        return {
            "validation": "I hear you. What you're experiencing is valid, and it's okay to feel overwhelmed.",
            "category": "mixed",
            "energy_impact": "medium",
            "actionable_items": [],
            "processing_items": ["Take a moment to breathe", "It's okay to feel this way"],
            "supportive_tags": ["self-care", "processing", "valid-feelings"],
            "gentle_reframe": "Sometimes our minds need to empty out. This is part of the process.",
            "next_steps": "Take a deep breath and know you don't have to figure it all out right now"
        }

    def _fallback_plan(self) -> Dict:
        """Fallback plan if AI processing fails"""
        return {
            "title": "Gentle Next Steps",
            "description": "Let's take this one small step at a time",
            "recommended_energy": "low",
            "steps": [
                {
                    "title": "Take a breath",
                    "description": "Center yourself for a moment",
                    "micro_tasks": ["Close your eyes", "Take 3 deep breaths", "Notice how you feel"],
                    "energy_cost": "low",
                    "estimated_minutes": 2
                }
            ]
        }


class NeuroFriendlyFeatures:
    """Specialized features for neurodivergent users"""

    @staticmethod
    def suggest_break_time(session_duration: int, energy_level: str) -> Dict:
        """Suggest breaks based on neurodivergent attention patterns"""
        break_suggestions = {
            'high': 25,  # Pomodoro-style
            'medium': 15,  # Shorter bursts
            'low': 10   # Very gentle approach
        }

        return {
            'suggested_break_interval': break_suggestions.get(energy_level, 15),
            'break_activities': [
                'Deep breathing for 2 minutes',
                'Stretch your arms and neck',
                'Drink some water',
                'Look at something far away',
                'Quick walk around the room'
            ],
            'message': 'Your brain has been working hard. A small break helps it process better.'
        }

    @staticmethod
    def adapt_interface(user_preferences: Dict) -> Dict:
        """Adapt interface based on sensory preferences"""
        return {
            'reduce_motion': user_preferences.get('prefers_minimal_motion', False),
            'high_contrast': user_preferences.get('prefers_high_contrast', False),
            'larger_text': user_preferences.get('prefers_larger_text', False),
            'quiet_mode': user_preferences.get('quiet_mode', False),
            'css_classes': {
                'motion': 'motion-reduce' if user_preferences.get('prefers_minimal_motion') else '',
                'contrast': 'high-contrast' if user_preferences.get('prefers_high_contrast') else '',
                'text': 'text-lg' if user_preferences.get('prefers_larger_text') else ''
            }
        }

    @staticmethod
    def executive_function_support(task_complexity: str) -> Dict:
        """Provide executive function scaffolding"""
        if task_complexity == 'high':
            return {
                'break_down_further': True,
                'add_time_estimates': True,
                'suggest_body_doubling': True,
                'include_prep_steps': True,
                'reminder_frequency': 'frequent',
                'message': 'This looks like a big task. Let\'s break it into tiny pieces.'
            }
        elif task_complexity == 'medium':
            return {
                'add_time_estimates': True,
                'gentle_reminders': True,
                'reminder_frequency': 'moderate',
                'message': 'You\'ve got this. Take it step by step.'
            }
        else:
            return {
                'gentle_reminders': True,
                'reminder_frequency': 'light',
                'message': 'This is manageable. Just one thing at a time.'
            }

    @staticmethod
    def get_time_context() -> str:
        """Get neurodivergent-friendly time context"""
        from datetime import datetime

        now = datetime.now()
        hour = now.hour

        if 5 <= hour < 12:
            return "Good morning"
        elif 12 <= hour < 17:
            return "Good afternoon"
        elif 17 <= hour < 21:
            return "Good evening"
        else:
            return "Late night check-in"

    @staticmethod
    def generate_celebration_message(celebration_type: str, context: Optional[Dict] = None) -> str:
        """Generate encouraging celebration messages"""
        context = context or {}

        messages = {
            'note_captured': [
                "Beautiful work! You've captured that thought.",
                "Great job getting that out of your head!",
                "You're building your thought garden.",
            ],
            'plan_created': [
                "Wonderful! You've made a plan. That's powerful.",
                "Look at you, turning thoughts into action!",
                "You're moving from overwhelm to clarity.",
            ],
            'step_completed': [
                "Yes! You did it!",
                "One step closer. You're amazing.",
                "Progress! This is how change happens.",
            ],
            'plan_completed': [
                "Incredible! You completed a whole plan!",
                "Look what you accomplished! Seriously amazing.",
                "You turned overwhelm into achievement. Celebrate this!",
            ],
            'energy_check': [
                "Thank you for checking in with yourself.",
                "Self-awareness is a superpower. Good job.",
                "Taking time to understand your energy is wise.",
            ],
        }

        import random
        message_list = messages.get(celebration_type, ["Great work!"])
        return random.choice(message_list)
