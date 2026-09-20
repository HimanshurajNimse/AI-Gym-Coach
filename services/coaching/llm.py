import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()


class LLMCoach:
    def __init__(self):
        api_key = os.getenv("GROQ_API_KEY")

        if not api_key:
            raise ValueError("GROQ_API_KEY is missing from .env")

        self.client = Groq(api_key=api_key)
        self.model = "groq/compound-mini"

    def give_feedback(self, event, exercise=None, issue=None):
        prompt = f"""
You are an AI gym coach.

Event: {event}
Exercise: {exercise or 'General Workout'}
Issue: {issue or "No specific issue"}

Give one short, natural spoken coaching instruction.
Maximum 2 sentences.
Do not use markdown, bullet points, emojis, or technical explanations.
"""

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": "You are a concise and encouraging gym coach."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.6,
            max_tokens=100
        )

        return response.choices[0].message.content.strip()

    def generate_workout_summary(self, exercise, reps, sets, form_issues):
        issues_str = "\n".join(set(form_issues)) if form_issues else "Perfect form, no issues!"
        prompt = f"""
You are an AI gym coach giving a final post-workout summary.

Exercise: {exercise}
Total Sets: {sets}
Total Reps: {reps}
Form Notes: 
{issues_str}

Write a short, engaging 2-3 sentence summary reviewing their performance. Praise their effort and give them one actionable tip based on their form notes for next time. Do not use markdown bullet points, keep it conversational.
"""
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": "You are a highly motivating AI gym coach."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.7,
            max_tokens=150
        )
        return response.choices[0].message.content.strip()