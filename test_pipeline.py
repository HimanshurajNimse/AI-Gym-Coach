import os
from dotenv import load_dotenv
load_dotenv()

from services.coaching.llm import LLMCoach
from services.coaching.tts import TextToSpeech
from services.coaching.voice_pipeline import VoicePipeline

try:
    print("Initializing LLMCoach...")
    llm = LLMCoach()
    
    print("Initializing TTS...")
    tts = TextToSpeech()
    
    pipeline = VoicePipeline(llm=llm, tts=tts)
    
    print("Processing event...")
    result = pipeline.process_event("workout_started", "Squats", {})
    if result:
        audio, text = result
        print(f"Feedback: {text}")
        print(f"Audio bytes length: {len(audio)}")
    else:
        print("No result returned.")

except Exception as e:
    import traceback
    traceback.print_exc()
