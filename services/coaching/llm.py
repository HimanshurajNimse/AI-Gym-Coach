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
        self.model = "llama-3.3-70b-versatile"

    def give_feedback(self, event, issue=None):
        prompt = f"""
You are an AI gym coach.

Exercise: {event}
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