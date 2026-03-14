from __future__ import annotations

# Central configuration for the Jarvis-style calculator.

APP_NAME = "Universal AI Math Voice Assistant"

# Speech recognition
LISTEN_TIMEOUT = 5.0
PHRASE_TIME_LIMIT = 8.0
AMBIENT_NOISE_DURATION = 1.0
RECOGNITION_LANGUAGE = "en-IN"

# Text-to-speech
TTS_RATE = 175
TTS_VOLUME = 0.9
TTS_VOICE_ID = None  # Set to a specific voice id string if desired.

# Math
PLOT_RANGE = (-10, 10)
PLOT_POINTS = 400

# Ollama integration
OLLAMA_ENABLED = True
OLLAMA_TIMEOUT = 12
OLLAMA_MODEL_PRIORITY = ["deepseek-coder", "llama3", "mixtral", "mistral", "codellama"]

# Language detection
LANGUAGE_DETECT_ENABLED = True
LANGUAGE_DETECT_FALLBACK = "en"
