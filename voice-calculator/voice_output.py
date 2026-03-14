from __future__ import annotations

import pyttsx3

from config import TTS_RATE, TTS_VOLUME, TTS_VOICE_ID


class VoiceOutput:
    def __init__(self) -> None:
        self.engine = pyttsx3.init()
        self.engine.setProperty("rate", TTS_RATE)
        self.engine.setProperty("volume", TTS_VOLUME)
        if TTS_VOICE_ID:
            self.engine.setProperty("voice", TTS_VOICE_ID)

    def speak(self, text: str) -> None:
        if not text:
            return
        self.engine.say(text)
        self.engine.runAndWait()
