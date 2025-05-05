#!/usr/bin/env python3
"""
sd_picker_agent_openai.py
—————————
Given an LLVM‑IR file, ask an OpenAI chat model (e.g. gpt‑4o) to pick exactly
THREE candidate values per OpenMP knob that are likely to minimise runtime.

Author: Md Arafat Hossain
"""

from pathlib import Path
import os, re, json, argparse, openai
from llvmlite import binding as llvm
import json, math, tempfile, subprocess, os
from collections import Counter

# --------------------------------------------------------------------------- #
# 0)  USER‑EDITABLE CONSTANTS                                                 #
# --------------------------------------------------------------------------- #
DEFAULT_MODEL  = "gpt-4o-mini"            # or gpt-4o, gpt-4-turbo, gpt-3.5-turbo
MAX_TOKENS_RSP = 256                      # tokens *in the reply*

SEARCH_SPACE = {
    "OMP_NUM_THREADS": [4, 8, 12, 16, 20, 24, 28, 32, 36, 40, 44, 48],
    "OMP_PROC_BIND":  ["true", "false", "close", "spread"],
    "OMP_SCHEDULE":   ["static", "dynamic", "guided"]
}

llvm.initialize()
llvm.initialize_native_target()
llvm.initialize_native_asmprinter()

def _get_loop_depth(fn_ir: str) -> int:
    """
    Pipe the function IR through `opt -loop-info -analyze`
    and count 'Loop at depth = X' lines.  Requires LLVM opt.
    """
    with tempfile.NamedTemporaryFile(delete=False, mode="w") as tmp:
        tmp.write(fn_ir)
        tmp_name = tmp.name
    try:
        out = subprocess.check_output(
            ["opt", "-loop-info", "-analyze", tmp_name],
            stderr=subprocess.STDOUT, text=True)
        return max((int(line.split()[-1])
                    for line in out.splitlines() if "depth =" in line),
                   default=0)
    finally:
        os.remove(tmp_name)

# --------------------------------------------------------------------------- #
# 1)  LIGHT STATIC FEATURE EXTRACTOR                                          #
# --------------------------------------------------------------------------- #
def extract_features(ir_src: str) -> dict:
    module = llvm.parse_assembly(ir_src)
    module.verify()

    # ------ 1) inspect the first (kernel) function -------
    func = next(f for f in module.functions if not f.is_declaration)

    counts = Counter()
    gep_unit_stride = True

    for block in func.blocks:
        for inst in block.instructions:
            opname = inst.opcode
            if opname in ("load", "store"):
                counts["mem"] += 1
            elif opname in ("fadd", "fmul", "fsub", "fdiv",
                            "add",  "mul",  "sub",  "udiv", "sdiv"):
                counts["flop"] += 1
            elif opname == "getelementptr":
                # Check first two indices:  0, idx  ⇒  unit stride
                idx_vals = list(inst.operands)[2:]
                if len(idx_vals) >= 1 and not idx_vals[0].is_constant or \
                   len(idx_vals) >= 2 and not idx_vals[1].is_constant:
                    gep_unit_stride = False

    mem_int     = counts["mem"] / max(1, counts["flop"])
    loop_depth  = _get_loop_depth(str(func))
    bound       = ("memory"  if mem_int > 2     else
                   "compute" if mem_int < 0.5   else
                   "mixed")

    return {
        "bound": bound,
        "mem_intensity": round(mem_int, 3),
        "loop_depth": loop_depth,
        "unit_stride": gep_unit_stride
    }

# --------------------------------------------------------------------------- #
# 2)  PROMPT TEMPLATES                                                        #
# --------------------------------------------------------------------------- #
# SYSTEM_MSG = "You are an HPC kernel seed‑picker."

# EXAMPLE_BLOCK = """
# EXAMPLE INPUT
# STATIC_FEATURES:
# {"bound":"memory","loop_depth":2}
# SEARCH_SPACE:
# {"OMP_NUM_THREADS":[4,8],"OMP_PROC_BIND":["true","close"],
#  "OMP_SCHEDULE":["static","dynamic"]}

# EXAMPLE OUTPUT
# {
#   "OMP_NUM_THREADS": [8,4,4],
#   "OMP_PROC_BIND": ["close","true","true"],
#   "OMP_SCHEDULE": ["dynamic","static","static"]
# }
# """.strip()

# USER_TEMPLATE = """
# LLVM IR:
# {features_json}

# SEARCH_SPACE:
# {search_json}

# EXPERIMENT_PLATFORM:
# The Intel shared-memory machine has a 2x Intel Xeon Platinum 8168 processors
# with a total of 48 (2x24) physical cores and 2 hyperthreads per
# core (i.e., total 96 logical cores)

# TASK:
# Choose exactly THREE candidate values **per knob** that you believe will
# minimise runtime.

# FORMAT (return ONLY this, no markdown, no prose):
# {{
#   "OMP_NUM_THREADS": [<int1>, <int2>, <int3>],
#   "OMP_PROC_BIND" : ["<str1>", "<str2>", "<str3>"],
#   "OMP_SCHEDULE"  : ["<str1>", "<str2>", "<str3>"]
# }}

# • Rank values best→worst inside each list.
# • Think step‑by‑step **internally**, then output only the JSON.
# """.strip()

SYSTEM_MSG = """
You are an HPC kernel *seed‑picker* for an Intel Skylake‑SP node
with **2 × 24 physical cores, SMT on (96 logical cores)**.

Choose exactly **three** candidate values for each OpenMP knob that you
believe will minimise wall‑clock runtime **on this hardware**, given:

  • STATIC_FEATURES   – contains
        "bound"          ∈ {"compute","memory","mixed"}
        "mem_intensity"  – numeric load/store ÷ arithmetic ratio
        "loop_depth"     – nesting depth (≥2 means perfectly‑nested)
  • SEARCH_SPACE       – legal values for each knob

**Heuristics you MUST follow**

1. Thread count (`OMP_NUM_THREADS`)
   ────────────────────────────────
   a. Always include **48** (1 thread / physical‑core)  
      – list it *first* if `"bound":"compute"` or `"loop_depth">=2`.  
   b. If 48 is present and `"bound":"compute"`, put **44** second
      (leaves 2 cores free per socket).  
   c. Pick a lower value (32→24→16) only as third choice *unless*
      `"bound":"memory"` *and* `mem_intensity > 2`.

2. `OMP_PROC_BIND`
   • `"close"` first (cache locality), `"spread"` second (bandwidth),
     `"true"` third as portable fallback.

3. `OMP_SCHEDULE`
   • If `loop_depth >= 2`  → `"static"` first.  
   • Otherwise             → `"guided"` first, `"dynamic"` second.

**Output ONLY the JSON** in the exact shape below, ranked best → third:

{
  "OMP_NUM_THREADS": [<int1>, <int2>, <int3>],
  "OMP_PROC_BIND" : ["<str1>", "<str2>", "<str3>"],
  "OMP_SCHEDULE"  : ["<str1>", "<str2>", "<str3>"]
}

Think step‑by‑step internally, then emit just that JSON.
"""

EXAMPLE_BLOCK = """
EXAMPLE 1  (compute‑bound, deep loops)
STATIC_FEATURES:
{"bound":"compute","mem_intensity":0.35,"loop_depth":3}
SEARCH_SPACE:
{"OMP_NUM_THREADS":[4,8,16,24,32,40,44,48],
 "OMP_PROC_BIND":["true","close","spread"],
 "OMP_SCHEDULE":["static","dynamic","guided"]}

EXPECTED OUTPUT
{
  "OMP_NUM_THREADS": [48,44,32],
  "OMP_PROC_BIND": ["close","spread","true"],
  "OMP_SCHEDULE": ["static","guided","dynamic"]
}

EXAMPLE 2  (memory‑bound, shallow loop)
STATIC_FEATURES:
{"bound":"memory","mem_intensity":3.4,"loop_depth":1}
SEARCH_SPACE:
{"OMP_NUM_THREADS":[4,8,16,24,32,40,44,48],
 "OMP_PROC_BIND":["true","close","spread"],
 "OMP_SCHEDULE":["static","dynamic","guided"]}

EXPECTED OUTPUT
{
  "OMP_NUM_THREADS": [32,24,16],
  "OMP_PROC_BIND": ["spread","close","true"],
  "OMP_SCHEDULE": ["guided","dynamic","static"]
}
""".strip()

USER_TEMPLATE = """
LLVM IR FEATURES:
{features_json}

SEARCH_SPACE:
{search_json}

EXPERIMENT_PLATFORM:
Intel Xeon Platinum 8168 × 2 (24 cores/socket, SMT on, 96 logical cores)

TASK:
Return the **ranked triple** for each knob that you predict will run fastest.
Remember the heuristics and output **only** the JSON.
""".strip()


def build_messages(feats: dict) -> list[dict]:
    user = EXAMPLE_BLOCK + "\n\n" + USER_TEMPLATE.format(
        features_json=json.dumps(feats, separators=(",", ":")),
        search_json=json.dumps(SEARCH_SPACE, separators=(",", ":"))
    )
    return [
        {"role": "system", "content": SYSTEM_MSG},
        {"role": "user",   "content": user}
    ]

# --------------------------------------------------------------------------- #
# 3)  OpenAI Chat Completion call                                             #
# --------------------------------------------------------------------------- #
def call_openai(messages: list[dict],
                model: str,
                max_tokens_rsp: int) -> dict:
    rsp = openai.chat.completions.create(
        model          = model,
        messages       = messages,
        temperature    = 0.0,
        max_tokens     = max_tokens_rsp,
        stop           = ["}"]              # stop at first closing brace
    )
    text = rsp.choices[0].message.content
    json_block = text if text.endswith("}") else text.split("}")[0] + "}"
    try:
        return json.loads(json_block)
    except json.JSONDecodeError as e:
        raise RuntimeError(f"Bad JSON from OpenAI model:\n{text}") from e

# --------------------------------------------------------------------------- #
# 4)  MAIN DRIVER                                                             #
# --------------------------------------------------------------------------- #
def pick_seeds(ir_path: Path, model_name: str):
    ir_src  = ir_path.read_text()
    feats   = extract_features(ir_src)
    messages = build_messages(feats)

    print(f"Querying OpenAI model {model_name} …")
    seeds = call_openai(messages, model_name, MAX_TOKENS_RSP)
    print(json.dumps(seeds, indent=2))
    return seeds

# --------------------------------------------------------------------------- #
# 5)  CLI                                                                     #
# --------------------------------------------------------------------------- #
if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Seed picker via OpenAI API")
    ap.add_argument("--ir", required=True, help="Path to LLVM‑IR file")
    ap.add_argument("--openai_model", default=DEFAULT_MODEL,
                    help="OpenAI model id (e.g. gpt-4o, gpt-4o-mini)")
    ap.add_argument("--openai_key",   default=os.getenv("OPENAI_API_KEY"),
                    help="OpenAI API key (or set env OPENAI_API_KEY)")
    args = ap.parse_args()

    if not args.openai_key:
        ap.error("Missing API key.  Pass --openai_key or set OPENAI_API_KEY.")

    openai.api_key = args.openai_key
    pick_seeds(Path(args.ir), args.openai_model)
