from __future__ import annotations

import speech_recognition as sr

from config import LISTEN_TIMEOUT, PHRASE_TIME_LIMIT, RECOGNITION_LANGUAGE, AMBIENT_NOISE_DURATION


class SpeechEngine:
    def __init__(self) -> None:
        self.recognizer = sr.Recognizer()
        self.recognizer.dynamic_energy_threshold = True

    def listen(self, timeout: float | None = LISTEN_TIMEOUT, phrase_time_limit: float | None = PHRASE_TIME_LIMIT) -> str:
        with sr.Microphone() as source:
            print("Listening...")
            self.recognizer.adjust_for_ambient_noise(source, duration=AMBIENT_NOISE_DURATION)
            audio = self.recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)

        try:
            text = self.recognizer.recognize_google(audio, language=RECOGNITION_LANGUAGE)
            print("Heard:", text)
            return text.lower().strip()
        except sr.UnknownValueError:
            return ""
        except sr.RequestError:
            return ""

    def listen_with_retries(self, retries: int = 2) -> str:
        for _ in range(retries + 1):
            try:
                result = self.listen()
                if result:
                    return result
            except sr.WaitTimeoutError:
                pass
        return ""
