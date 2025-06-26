#!/usr/bin/env python3
"""
sd_picker_agent_openai.py   —   pure‑llvmlite static extractor + two‑turn LLM
"""

from pathlib import Path
import os, re, json, argparse, openai
from llvmlite import binding as llvm
from collections import Counter

# ─── Config ──────────────────────────────────────────────────────────────────
DEFAULT_MODEL    = "gpt-4o-mini"
MAX_TOKENS_REPLY = 256
SEARCH_SPACE = {
    "OMP_NUM_THREADS": [4, 8, 12, 16, 20, 24, 28, 32, 36, 40, 44, 48],
    "OMP_PROC_BIND":  ["true", "false", "close", "spread"],
    "OMP_SCHEDULE":   ["static", "dynamic", "guided"]
}
llvm.initialize(); llvm.initialize_native_target(); llvm.initialize_native_asmprinter()

# ─── 1. pure‑llvmlite feature extractor ─────────────────────────────────────
def extract_features(ir_src: str) -> dict:
    module = llvm.parse_assembly(ir_src); module.verify()
    func   = next(f for f in module.functions if not f.is_declaration)

    cnt = Counter(); vec_instr = 0; packed = 0; math_call = False

    for blk in func.blocks:
        for inst in blk.instructions:
            op = inst.opcode
            if op in ("load", "store"):
                cnt["mem"] += 1
            elif op in ("fadd","fmul","fsub","fdiv","add","mul","sub","udiv","sdiv"):
                cnt["flop"] += 1

            operands_list = list(inst.operands)

            if inst.type.is_vector or any(o.type.is_vector for o in operands_list):
                vec_instr += 1
            if inst.type.is_vector or (inst.type.is_array and inst.type.element.is_vector):
                packed += 1

            if op == "call" and operands_list:
                callee = operands_list[0]
                if hasattr(callee, "name") and callee.name in {
                        "sin","cos","exp","log","pow","sqrt","tanh"}:
                    math_call = True

    mem_int   = cnt["mem"] / max(1, cnt["flop"])
    bound     = "memory" if mem_int > 2 else "compute" if mem_int < .5 else "mixed"
    vec_ratio = vec_instr / max(1, cnt["mem"]+cnt["flop"])

    depths = [len(m.group(1)) for m in re.finditer(r"(\s*)br label", ir_src)]
    loop_depth = max(depths)//2 if depths else 0

    return {
        "bound": bound,
        "mem_intensity": round(mem_int,3),
        "loop_depth": loop_depth,
        "vector_ratio": round(vec_ratio,3),
        "packed_ratio": round(packed/max(1,vec_instr+cnt["mem"]+cnt["flop"]),3),
        "uses_math_lib": math_call
    }

# ─── 2. prompt pieces & heuristics (same as before) ─────────────────────────
SYSTEM_MSG = """
You are an HPC kernel *seed‑picker* for an Intel Skylake‑SP node
(2 × 24 physical cores, SMT on = 96 logical cores).  Use the heuristics below,
think step‑by‑step, then output three ranked candidates per knob.
"""
HEURISTICS = """
HEURISTICS
1. OMP_NUM_THREADS
   · Always include 48 (physical cores). Put it first if compute‑bound.
   · For memory‑bound (mem_intensity > 2) prefer 32/24/16.
   · 44 is a good second when compute‑bound.
2. OMP_PROC_BIND = ["close","spread","true"].
3. OMP_SCHEDULE
   · "static" first if loop_depth ≥ 2 and vector_ratio < 0.1, else "guided".
"""
USER_TEMPLATE = """
STATIC_FEATURES:
{feat}
SEARCH_SPACE:
{space}
TASK:
Return your **DRAFT** with reasoning.

REASON: <why>
DRAFT:
{{
  "OMP_NUM_THREADS": [...],
  "OMP_PROC_BIND" : [...],
  "OMP_SCHEDULE"  : [...]
}}
""".strip()
CRITIC_INSTR = "Reflect on your REASON and output ONLY the final JSON."

# ─── 3. OpenAI chat helpers ─────────────────────────────────────────────────
def chat(msgs, model):
    return openai.chat.completions.create(
        model=model, messages=msgs,
        temperature=0.0, max_tokens=MAX_TOKENS_REPLY,
        stop=["}"]).choices[0].message.content
def to_json(reply: str) -> dict:
    """
    Grab the FIRST {...} substring in the reply, tolerate leading fences,
    backticks, etc.  Raise if none found.
    """
    m = re.search(r"\{[^{}]*?(?:\{[^{}]*?\}[^{}]*?)*\}", reply, re.S)
    if not m:
        raise ValueError("Model reply contained no JSON block:\n" + reply)
    return json.loads(m.group(0))

# ─── 4. two‑turn picker ─────────────────────────────────────────────────────
def pick_seeds(ir: Path, model: str):
    feats = extract_features(ir.read_text())
    user1 = USER_TEMPLATE.format(
        feat=json.dumps(feats, separators=(",",":")),
        space=json.dumps(SEARCH_SPACE, separators=(",",":")))
    draft = chat(
        [{"role":"system","content":SYSTEM_MSG+HEURISTICS},
         {"role":"user"  ,"content":user1}], model)
    print("── DRAFT ──\n", draft, "\n")
    final = chat(
        [{"role":"system","content":SYSTEM_MSG},
         {"role":"assistant","content":draft},
         {"role":"user","content":CRITIC_INSTR}], model)
    seeds = to_json(final)
    print("── FINAL ──\n", json.dumps(seeds,indent=2)); return seeds

# ─── 5. CLI ─────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--ir", required=True); p.add_argument("--model", default=DEFAULT_MODEL)
    p.add_argument("--key", default=os.getenv("OPENAI_API_KEY"))
    ns = p.parse_args()
    if not ns.key: p.error("Set OPENAI_API_KEY or --key")
    openai.api_key = ns.key
    pick_seeds(Path(ns.ir), ns.model)
