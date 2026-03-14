from __future__ import annotations

import argparse

from config import APP_NAME
from graph_plotter import plot_expression
from math_engine import calculate, differentiate, integrate, solve_equation
from math_parser import ParseResult, parse
from memory_manager import MemoryManager
from ollama_controller import OllamaController
from speech_engine import SpeechEngine
from voice_output import VoiceOutput


class JarvisCalculator:
    def __init__(self) -> None:
        self.speech = SpeechEngine()
        self.voice = VoiceOutput()
        self.memory = MemoryManager()
        self.ollama = OllamaController()

    def handle(self, text: str) -> str:
        parsed = parse(text)

        if parsed.intent == "empty":
            return "I couldn't hear anything. Please try again."

        if parsed.intent == "exit":
            return "exit"

        if parsed.intent == "repeat":
            last = self.memory.last_result()
            if last is None:
                return "No previous result."
            return f"Last result is {last}"

        if parsed.intent == "clear_history":
            self.memory.clear()
            return "History cleared"

        if parsed.intent == "show_history":
            history = self.memory.history()
            if not history:
                return "History is empty"
            last = history[-1]
            return f"Last: {last.query} equals {last.result}"

        if parsed.incomplete:
            return "I heard an incomplete expression. Please say it again."

        if parsed.intent == "plot" and parsed.expression:
            error = plot_expression(parsed.expression)
            if error:
                return f"Plot error: {error}"
            return "Plot displayed"

        expression = parsed.expression or ""

        if parsed.needs_ollama:
            ollama_expr = self.ollama.convert_math(text)
            if ollama_expr:
                expression = ollama_expr

        if parsed.intent == "solve" and expression:
            result = solve_equation(expression)
            if not result.ok:
                return "I couldn't solve that equation."
            self.memory.add(expression, result.value)
            return f"Solution is {result.value}"

        if parsed.intent == "differentiate" and expression:
            result = differentiate(expression)
            if not result.ok:
                return "I couldn't differentiate that."
            self.memory.add(expression, result.value)
            return f"Derivative is {result.value}"

        if parsed.intent == "integrate" and expression:
            result = integrate(expression)
            if not result.ok:
                return "I couldn't integrate that."
            self.memory.add(expression, result.value)
            return f"Integral is {result.value}"

        if parsed.intent == "calculate" and expression:
            result = calculate(expression)
            if not result.ok:
                return "I couldn't understand the expression. Please try again."
            self.memory.add(expression, result.value)
            return f"The result is {result.value}"

        return "Sorry, I could not understand."

    def run_cli(self) -> None:
        self.voice.speak(f"{APP_NAME} started")

        while True:
            command = self.speech.listen_with_retries()
            if not command:
                self.voice.speak("I couldn't understand. Please try again.")
                continue

            response = self.handle(command)
            if response == "exit":
                self.voice.speak("Calculator closed")
                break

            print(response)
            self.voice.speak(response)


def main() -> None:
    parser = argparse.ArgumentParser(description=APP_NAME)
    parser.add_argument("--text", help="Run a single text command and exit")
    args = parser.parse_args()

    jarvis = JarvisCalculator()

    if args.text:
        response = jarvis.handle(args.text)
        print(response)
        return

    jarvis.run_cli()


if __name__ == "__main__":
    main()
