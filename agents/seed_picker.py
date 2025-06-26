import json
from typing import Dict, Any

class SeedPickerAgent:
    """Takes the prompt produced by PromptGenerationAgent, calls a (possibly
    smaller/faster) LLM, and returns a concrete config dict. The agent is fully
    modular: it understands only the prompt contract – *not* Programl or the
    orchestrator logic.
    """

    def __init__(self, model_name: str = "google/gemma-7b-it"):
        self.model_name = model_name

    def pick_parameters(self, prompt_text: str) -> Dict[str, Any]:
        messages = [
            {"role": "system", "content": "You are a helpful agent following the user's optimisation task."},
            {"role": "user", "content": prompt_text},
        ]
        raw_output = call_openrouter(self.model_name, messages, temperature=0.2)
        # We assume the Seed‑Picker returns either JSON or clearly marked code‑block JSON
        try:
            first_brace = raw_output.index("{")
            last_brace = raw_output.rindex("}") + 1
            param_json = raw_output[first_brace:last_brace]
            params = json.loads(param_json)
        except Exception as exc:
            raise ValueError(f"Failed to parse parameters from model output:\n{raw_output}") from exc
        return params