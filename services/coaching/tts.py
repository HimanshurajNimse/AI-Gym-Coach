from io import BytesIO
from gtts import gTTS

class TextToSpeech:
    def speak(self, text, lang="en"):
        text = (text or "").strip()

        if not text:
            return None

        buffer = BytesIO()
        gTTS(text=text, lang=lang).write_to_fp(buffer)

        audio_bytes = buffer.getvalue()
        print("TTS AUDIO SIZE:", len(audio_bytes))

        return audio_bytes