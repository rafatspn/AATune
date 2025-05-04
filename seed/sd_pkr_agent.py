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


# -----------------------------------------------------------------------------#
# 1.  Simple static‑feature extractor for LLVM‑IR (no external tools required). #
# -----------------------------------------------------------------------------#
def extract_static_features(ir_text: str) -> dict[str, float]:
    """
    Light weight heuristics that could be replaced by llvm-mca later
    """

    n_load  = len(re.findall(r"\bload\b",  ir_text))
    n_store = len(re.findall(r"\bstore\b", ir_text))
    n_mem   = n_load + n_store

    n_arith = len(re.findall(r"\b(add|mul|fadd|fmul|sub|fsub|div|fdiv)\b",
                             ir_text))

    # crude bound classification
    bound = ("memory" if n_mem > 2 * n_arith else
             "compute" if n_arith > 2 * n_mem else
             "mixed")

    # loop depth ≈ max indentation of 'br label'
    depths = [len(m.group(1)) for m in re.finditer(r"(\s*)br label", ir_text)]
    loop_depth = max(depths) // 2 if depths else 0   # 2‑space indent assumption

    return {
        "load_cnt": n_load,
        "store_cnt": n_store,
        "arith_cnt": n_arith,
        "bound": bound,
        "loop_depth": loop_depth
    }


# --------------------------------------------#
# 2.  Build the prompt for the Mistral model. #
# --------------------------------------------#
SYSTEM_PROMPT = (
    "You are an HPC kernel *seed‑picker*.\n"
    "Given static kernel features and the allowed knob values, return EXACTLY "
    "THREE candidate values **per knob** that you believe will minimise "
    "runtime.  Output JSON strictly in the form:\n"
    "{\n"
    "  \"OMP_NUM_THREADS\": [ ... 3 ints ... ],\n"
    "  \"OMP_PROC_BIND\" : [ ... 3 strings ... ],\n"
    "  \"OMP_SCHEDULE\"  : [ ... 3 strings ... ]\n"
    "}\n"
    "Rank inside each list best→worst.\n"
    "Do not add keys, commentary, or markdown."
)

def build_prompt(features: dict) -> str:
    search_space = {
        "omp_threads": [4, 8, 16, 24, 32, 40, 44, 48],
        "omp_proc_bind": ["true", "false", "close", "spread"],
        "omp_schedule": ["static", "dynamic", "guided"]
    }
    user_msg = {
        "static_features": features,
        "search_space": search_space,
        "require": "Return exactly 3 seed configs ranked best‑to‑worst."
    }
    return (f"<s>[INST] {SYSTEM_PROMPT}\n\n{json.dumps(user_msg, indent=2)} "
            "[/INST]")


# -----------------------------------------------------------------------------#
# 3.  Query the LLM and parse the JSON reply.                                   #
# -----------------------------------------------------------------------------#
def query_llm(prompt: str,
              model_path: str = "/lus/grand/projects/EE-ECP/araf/llms/mistral",
              max_new_tokens: int = 256,
              temperature: float = 0.1) -> dict:
    """
    Uses HuggingFace Transformers with a locally‑stored Mistral model.
    Assumes GGUF/LoRA or HF safetensors format that AutoModel* can load.
    """
    device = "cuda" if torch.cuda.is_available() else "cpu"

    tokenizer = AutoTokenizer.from_pretrained(model_path)
    model = AutoModelForCausalLM.from_pretrained(model_path,
                                                 torch_dtype=torch.float16,
                                                 device_map=device)

    ids = tokenizer.encode(prompt, return_tensors="pt").to(device)

    streamer = TextStreamer(tokenizer)
    out = model.generate(
        ids,
        max_new_tokens=max_new_tokens,
        temperature=temperature,
        do_sample=False,
        streamer=streamer
    )
    response = tokenizer.decode(out[0][ids.size(-1):], skip_special_tokens=True)

    # Find the first { ... } JSON block in the response
    match = re.search(r"\{.*\}", response, re.S)
    if not match:
        raise ValueError("LLM reply did not contain JSON:\n" + response)

    return json.loads(match.group(0))


# --------------------------------------------#
# 4.  High‑level utility function             #
# --------------------------------------------#
def pick_seeds(ir_file: str | Path) -> list[dict]:
    ir_text = Path(ir_file).read_text()
    features = extract_static_features(ir_text)
    prompt   = build_prompt(features)
    reply    = query_llm(prompt)
    seeds    = reply["seeds"]

    print("LLM‑chosen seed configurations:")
    for cfg in seeds:
        print(cfg)
    return seeds


# -----------------------------------------------------------------------------#
# 5.  CLI glue                                                                  #
# -----------------------------------------------------------------------------#
if __name__ == "__main__":
    import argparse
    argp = argparse.ArgumentParser(description="Pick warm‑start seeds "
                                               "for an OpenMP kernel.")
    argp.add_argument("-ir", help="Path to LLVM‑IR file")
    argp.add_argument("-model", default=("/lus/grand/projects/EE-ECP/araf/llms/"
                                          "mistral"),
                      help="HF or GGUF folder for the Mistral model")
    ns = argp.parse_args()

    pick_seeds(ns.ir)
