#!/usr/bin/env python3
"""
sd_picker_agent.py

Given an LLVM‑IR file, ask a local Mistral‑style LLM to emit **3 warm‑start
configurations** (one per parameter) that are likely to minimise execution time.

Author: Md Arafat Hossain
"""

from pathlib import Path
import json
import re
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, TextStreamer

MODEL_PATH="/lus/grand/projects/EE-ECP/araf/llms/mistral"

SEARCH_SPACE = {
    "OMP_NUM_THREADS": [4, 8, 16, 24, 32, 40, 48],
    "OMP_PROC_BIND":  ["true", "false", "close", "spread"],
    "OMP_SCHEDULE":   ["static", "dynamic", "guided"]
}
MAX_NEW_TOKENS = 256


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


def build_prompt(feats: dict, tok) -> str:
    user = EXAMPLE_BLOCK + "\n\n" + USER_TEMPLATE.format(
        features_json=json.dumps(feats, separators=(",", ":")),
        search_json=json.dumps(SEARCH_SPACE, separators=(",", ":"))
    )
    return tok.apply_chat_template(
        [{"role": "system", "content": SYSTEM_MSG},
         {"role": "user",   "content": user}],
        tokenize=False
    )

def call_llm(prompt: str, tok, model):
    inputs = tok.encode(prompt, return_tensors="pt").to(model.device)
    brace_id = tok.convert_tokens_to_ids("}")

    gen_out = model.generate(
        inputs,
        max_new_tokens=MAX_NEW_TOKENS,
        temperature=0.0,        # deterministic
        do_sample=False,
        eos_token_id=brace_id   # stop at first closing brace
    )
    text = tok.decode(gen_out[0][inputs.size(-1):], skip_special_tokens=True)

    # Ensure we captured the closing brace
    json_block = text if text.endswith("}") else text.split("}")[0] + "}"
    try:
        return json.loads(json_block)
    except json.JSONDecodeError as e:
        raise RuntimeError(f"Bad JSON from LLM:\n{text}") from e

def pick_seeds(ir_path: Path):
    ir_src  = ir_path.read_text()
    feats   = extract_features(ir_src)

    print("Loading Mistral model locally...")
    tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH)
    model = AutoModelForCausalLM.from_pretrained(
        MODEL_PATH, 
        torch_dtype=torch.float16, 
        device_map="auto"
    )
    print("Model loaded successfully!\n")

    prompt  = build_prompt(feats, tokenizer)
    seeds   = call_llm(prompt, tokenizer, model)

    print(json.dumps(seeds, indent=2))
    return seeds


if __name__ == "__main__":
    import argparse
    argp = argparse.ArgumentParser(description="Pick warm‑start seeds "
                                               "for an OpenMP kernel.")
    argp.add_argument("-ir", help="Path to LLVM‑IR file")
    argp.add_argument("-model", default=("/lus/grand/projects/EE-ECP/araf/llms/mistral"), help="HF or GGUF folder for the Mistral model", required=False)
    ns = argp.parse_args()

    pick_seeds(Path(ns.ir))
