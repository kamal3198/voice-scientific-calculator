from __future__ import annotations

import subprocess
from typing import List, Optional

from config import OLLAMA_ENABLED, OLLAMA_MODEL_PRIORITY, OLLAMA_TIMEOUT


class OllamaController:
    def __init__(self) -> None:
        self._cached_model: Optional[str] = None

    def list_models(self) -> List[str]:
        if not OLLAMA_ENABLED:
            return []
        try:
            result = subprocess.run(
                ["ollama", "list"],
                capture_output=True,
                text=True,
                timeout=OLLAMA_TIMEOUT,
                check=False,
            )
            if result.returncode != 0:
                return []
            lines = [line.strip() for line in result.stdout.splitlines() if line.strip()]
            if not lines:
                return []
            models = []
            for line in lines[1:]:
                parts = line.split()
                if parts:
                    models.append(parts[0])
            return models
        except Exception:
            return []

    def choose_best_model(self) -> Optional[str]:
        if self._cached_model:
            return self._cached_model

        models = self.list_models()
        if not models:
            return None

        for preferred in OLLAMA_MODEL_PRIORITY:
            for model in models:
                if model.startswith(preferred):
                    self._cached_model = model
                    return model

        self._cached_model = models[0]
        return self._cached_model

    def convert_math(self, text: str) -> Optional[str]:
        if not OLLAMA_ENABLED:
            return None

        model = self.choose_best_model()
        if not model:
            return None

        prompt = (
            "Convert the spoken math into a valid Python/SymPy expression. "
            "Return ONLY the expression, no words."
            f"\nInput: {text}\nExpression:"
        )

        try:
            result = subprocess.run(
                ["ollama", "run", model, prompt],
                capture_output=True,
                text=True,
                timeout=OLLAMA_TIMEOUT,
                check=False,
            )
            if result.returncode != 0:
                return None
            output = result.stdout.strip()
            return output.splitlines()[-1].strip() if output else None
        except Exception:
            return None
