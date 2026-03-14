from __future__ import annotations

from speech_engine import listen, speak
from math_engine import calculate


def run() -> None:
    speak("Voice scientific calculator started")

    while True:
        command = listen()

        if not command:
            continue

        if "exit" in command or "quit" in command:
            speak("Calculator closed")
            break

        result = calculate(command)
        print("Result:", result)
        speak(f"The result is {result}")
