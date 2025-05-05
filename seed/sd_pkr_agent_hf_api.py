#!/usr/bin/env python3
"""
sd_picker_agent_hf.py

Given an LLVM‑IR file, query a *remote* Hugging Face model (e.g.
`mistralai/Mistral‑7B‑Instruct‑v0.2`) and return exactly three candidate values
per OpenMP knob in strict JSON form.

Author: Md Arafat Hossain
"""

from pathlib import Path
import json, re, argparse, os
from huggingface_hub import InferenceClient   # pip install huggingface_hub

# --------------------------------------------------------------------------- #
# 0)  USER‑EDITABLE CONSTANTS                                                 #
# --------------------------------------------------------------------------- #
# MODEL_ID  = "mistralai/Mistral-7B-Instruct-v0.2"
# HF_TOKEN  = os.getenv("HF_TOKEN")        # set env var or pass --hf_token
MAX_TOKENS = 256

SEARCH_SPACE = {
    "OMP_NUM_THREADS": [4, 8, 16, 24, 32, 40, 44, 48],
    "OMP_PROC_BIND":  ["true", "false", "close", "spread"],
    "OMP_SCHEDULE":   ["static", "dynamic", "guided"]
}

# --------------------------------------------------------------------------- #
# 1)  LIGHT STATIC FEATURE EXTRACTOR                                          #
# --------------------------------------------------------------------------- #
def extract_features(ir_src: str) -> dict:
    n_load   = len(re.findall(r"\bload\b",  ir_src))
    n_store  = len(re.findall(r"\bstore\b", ir_src))
    n_arith  = len(re.findall(r"\b(add|fadd|sub|mul|fmul|div|fdiv)\b", ir_src))
    mem_int  = (n_load + n_store) / max(1, n_arith)

    indent   = [len(m.group(1)) for m in re.finditer(r"(\s*)br label", ir_src)]
    loop_depth = max(indent) // 2 if indent else 0

    bound = ("memory" if mem_int > 2
             else "compute" if mem_int < 0.5
             else "mixed")
    return {"bound": bound,
            "mem_intensity": round(mem_int, 2),
            "loop_depth": loop_depth}

# --------------------------------------------------------------------------- #
# 2)  PROMPT TEMPLATES (unchanged)                                            #
# --------------------------------------------------------------------------- #
SYSTEM_MSG = "You are an HPC kernel seed‑picker."

EXAMPLE_BLOCK = """
EXAMPLE INPUT
STATIC_FEATURES:
{"bound":"memory","loop_depth":2}
SEARCH_SPACE:
{"OMP_NUM_THREADS":[4,8],"OMP_PROC_BIND":["true","close"],
 "OMP_SCHEDULE":["static","dynamic"]}

EXAMPLE OUTPUT
{
  "OMP_NUM_THREADS": [8,4,4],
  "OMP_PROC_BIND": ["close","true","true"],
  "OMP_SCHEDULE": ["dynamic","static","static"]
}
""".strip()

USER_TEMPLATE = """
STATIC_FEATURES:
{features_json}

SEARCH_SPACE:
{search_json}

TASK:
Choose exactly THREE candidate values **per knob** that you believe will
minimise runtime.

FORMAT (return ONLY this, no markdown, no prose):
{{
  "OMP_NUM_THREADS": [<int1>, <int2>, <int3>],
  "OMP_PROC_BIND" : ["<str1>", "<str2>", "<str3>"],
  "OMP_SCHEDULE"  : ["<str1>", "<str2>", "<str3>"]
}}

• Rank values best→worst inside each list.
• Think step‑by‑step **internally**, then output only the JSON.
""".strip()

def build_prompt(feats: dict) -> str:
    user = EXAMPLE_BLOCK + "\n\n" + USER_TEMPLATE.format(
        features_json=json.dumps(feats, separators=(",", ":")),
        search_json=json.dumps(SEARCH_SPACE, separators=(",", ":"))
    )
    # ChatML‑style prompt (system / user)
    return f"<s>[INST] <<SYS>>\n{SYSTEM_MSG}\n<</SYS>>\n\n{user} [/INST]"

# --------------------------------------------------------------------------- #
# 3)  CALL HUGGING FACE INFERENCE API                                         #
# --------------------------------------------------------------------------- #
def call_hf_api(prompt: str, model_id: str, hf_token: str) -> dict:
    client = InferenceClient(model=model_id, token=hf_token)

    # stop sequence '}' keeps the model from babbling after JSON
    response = client.text_generation(
        prompt,
        max_new_tokens=MAX_TOKENS,
        temperature=0.0,
        stop_sequences=["}"]
    )
    text = response.text
    json_block = text if text.endswith("}") else text.split("}")[0] + "}"
    try:
        return json.loads(json_block)
    except json.JSONDecodeError as e:
        raise RuntimeError(f"Bad JSON from model:\n{text}") from e

# --------------------------------------------------------------------------- #
# 4)  MAIN DRIVER                                                             #
# --------------------------------------------------------------------------- #
def pick_seeds(ir_path: Path, model_id: str, token: str):
    ir_src  = ir_path.read_text()
    feats   = extract_features(ir_src)
    prompt  = build_prompt(feats)

    print(f"Querying Hugging Face model {model_id} …")
    seeds   = call_hf_api(prompt, model_id, token)
    print(json.dumps(seeds, indent=2))
    return seeds

# --------------------------------------------------------------------------- #
# 5)  CLI                                                                     #
# --------------------------------------------------------------------------- #
if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Seed picker via HF Inference API")
    ap.add_argument("--ir", required=True, help="Path to LLVM‑IR file")
    ap.add_argument("--model_id", help="HF model repo ID (e.g. mistralai/Mistral‑7B‑Instruct‑v0.2)")
    ap.add_argument("--hf_token", help="Hugging Face access token; else set env HF_TOKEN")
    args = ap.parse_args()

    if not args.hf_token:
        ap.error("HF token missing.  Set --hf_token or environment variable HF_TOKEN")

    pick_seeds(Path(args.ir), args.model_id, args.hf_token)
