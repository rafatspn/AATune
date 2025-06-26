import json
import os
import time
from typing import Dict, List, Any, Tuple
import requests
from pathlib import Path
from prompt_gen import PromptGenerationAgent
from seed_picker import SeedPickerAgent
from dotenv import load_dotenv

load_dotenv()

MAX_PROMPT_TOKENS = os.getenv('MAX_PROMPT_TOKENS') 
OPENROUTER_ENDPOINT = os.getenv('OPEN_ROUTER_URL')
OPENROUTER_API_KEY = os.getenv('OPENROUTER_API_KEY')

def call_openrouter(model: str, messages: List[Dict[str, str]], temperature: float = 0.4, **kwargs) -> str:
    if OPENROUTER_API_KEY is None:
        raise EnvironmentError("OPENROUTER_API_KEY environment variable not set.")

    headers = {"Authorization": f"Bearer {OPENROUTER_API_KEY}", "Content-Type": "application/json"}
    payload = {"model": model, "messages": messages, "temperature": temperature}
    payload.update(kwargs)
    response = requests.post(OPENROUTER_ENDPOINT, headers=headers, json=payload, timeout=180)
    response.raise_for_status()
    return response.json()["choices"][0]["message"]["content"]

# def evaluate_kernel(params: Dict[str, Any], correct_result: List[Any] | Any) -> Tuple[bool, float]:
#     """Simulate running the kernel under *params* and checking correctness.

#     Replace this with actual compilation + measurement code that launches the
#     kernel on the target system. The example simply sleeps and fakes numbers.
#     """
#     time.sleep(0.2)  # pretend compile/runtime cost
#     import random
#     is_correct = random.choice([True, False])  # replace with real check
#     metric = random.uniform(0.5, 5.0)          # lower is better
#     return is_correct, metric

# class OptimisationOrchestrator:
#     """High‑level driver gluing both agents + verification loop.

#     ‑ *max_attempts* is capped at 5, per the user requirement.
#     ‑ On success the final prompt is written to *final_prompt.txt*.
#     """

#     def __init__(
#         self,
#         pg_agent: PromptGenerationAgent,
#         sp_agent: SeedPickerAgent,
#         max_attempts: int = 5,
#         prompt_out_path: str = "final_prompt.txt",
#     ):
#         self.pg_agent = pg_agent
#         self.sp_agent = sp_agent
#         self.max_attempts = max_attempts
#         self.prompt_out_path = prompt_out_path

#     def optimise(
#         self,
#         programl_json: Dict[str, Any],
#         machine_info: Dict[str, Any],
#         config_space: Dict[str, List[Any]],
#         correct_result: Any,
#     ) -> Dict[str, Any]:
#         """Returns the best parameter set found (early exit if perfect)."""

#         feedback: str | None = None
#         best_params: Dict[str, Any] | None = None
#         best_metric: float = float("inf")

#         for attempt in range(self.max_attempts):
#             # 1) Craft or refine prompt
#             prompt_txt = self.pg_agent.generate_prompt(
#                 programl_graph=programl_json,
#                 machine_info=machine_info,
#                 config_space=config_space,
#                 attempt_idx=attempt,
#                 previous_feedback=feedback,
#             )

#             # 2) Ask seed picker for params
#             params = self.sp_agent.pick_parameters(prompt_txt)

#             # 3) Evaluate
#             is_correct, metric_val = evaluate_kernel(params, correct_result)
#             feedback = (
#                 f"Attempt {attempt + 1}: correctness={is_correct}; objective={metric_val:.4f}"
#             )
#             print(feedback)

#             # 4) Keep best
#             if is_correct and metric_val < best_metric:
#                 best_metric = metric_val
#                 best_params = params

#             # 5) Early exit if perfect & short‑circuit
#             if is_correct:
#                 print("✅   Found correct parameter subset – stopping early.")
#                 # Persist final prompt
#                 with open(self.prompt_out_path, "w", encoding="utf-8") as fp:
#                     fp.write(prompt_txt)
#                 return best_params or params

#         print("⚠️   Reached maximum attempts; returning best‑seen parameters (may be incorrect).")
#         return best_params or params

if __name__ == "__main__":
    with open(Path('programl/3mm_kernel_p1.json').resolve(), 'r') as f:
        graph = json.load(f)

    machine = {
        "cpu": "AMD EPYC 9654",
        "num_sockets": 2,
        "cores_per_socket": 96,
        "l3_cache_per_socket": "256 MB",
        "memory": "512 GB DDR5",
        "os": "Ubuntu 22.04",
    }

    omp_space = {
        "OMP_NUM_THREADS": [4, 8, 16, 32, 64, 96, 128, 192],
        "OMP_SCHEDULE": ["static", "dynamic", "guided"],
        "OMP_PROC_BIND": ["true", "false"],
        "OMP_PLACES": ["cores", "sockets"],
    }

    correct = "<<reference checksum or output>>"

    print(MAX_PROMPT_TOKENS)
    print(OPENROUTER_API_KEY)
    print(OPENROUTER_ENDPOINT)

    # pg = PromptGenerationAgent(model_name="openai/gpt-4o-mini")
    # sp = SeedPickerAgent(model_name="google/gemma-7b-it")
    # orchestrator = OptimisationOrchestrator(pg, sp)
    # best = orchestrator.optimise(graph, machine, omp_space, correct)
    # print("Best parameters:", best)
