import json
from typing import Dict, List, Any
import tiktoken
import programl as pg

class PromptGenerationAgent:
    def __init__(self, model_name: str = "openai/gpt-4o"):
        self.model_name = model_name

    def generate_prompt(
        self,
        programl_graph: Dict[str, Any],
        machine_info: Dict[str, Any],
        config_space: Dict[str, List[Any]],
        attempt_idx: int = 0,
        previous_feedback: str | None = None,
    ) -> str:
        messages: List[Dict[str, str]] = []

        sys_prompt = (
            "You are an expert HPC performance engineer skilled at crafting"
            " *concise yet complete* optimisation briefs for other autonomous"
            " agents. Your job: write a prompt for a downstream *Seed‑Picker Agent*"
            " that will choose OpenMP parameter values (thread counts, schedule"
            " types, etc.) for the supplied kernel. 1) Summarise the kernel's"
            " structure and hotspots from the Programl graph, 2) list the target"
            " hardware, 3) list the *entire* configuration search space, 4) state"
            " the optimisation objective (min exec‑time subject to correctness),"
            " 5) specify output JSON schema the seed‑picker must follow."
            " If feedback from previous attempt is included, integrate it and"
            " refine the prompt so the seed‑picker avoids earlier mistakes."
        )
        messages.append({"role": "system", "content": sys_prompt})

        user_content = (
            f"### Programl Graph (abridged)\n{json.dumps(programl_graph, indent=2)[:12000]}\n\n"  # truncate for token safety
            f"### Machine Info\n{json.dumps(machine_info, indent=2)}\n\n"
            f"### Config Space\n{json.dumps(config_space, indent=2)}\n\n"
        )
        if previous_feedback:
            user_content += f"### Verification Feedback from Attempt {attempt_idx}➔ {previous_feedback}\n"

        user_content += (
            "Please write the prompt now. Remember: the prompt must stand alone;"
            " *nothing* external should be required by the seed‑picker."
        )

        messages.append({"role": "user", "content": user_content})

        prompt_text = call_openrouter(self.model_name, messages)
        return prompt_text
    

class PromptGenerationAgent:
    def __init__(self, model_name: str = "openai/gpt-4o-mini", openrouter_url:str='', openrouter_key:str='', max_prompt_tokens: int=8000):
        self.model_name = model_name
        self.url = openrouter_url
        self.key = openrouter_key
        self.max_prompt_token = max_prompt_tokens

    def n_tokens(text: str, model: str = "gpt-4o-mini") -> int:
        try:
            enc = tiktoken.encoding_for_model(model)
            return len(enc.encode(text))
        except ImportError:
            # fallback: estimate 4 chars ≈ 1 token
            return max(1, len(text) // 4)

    def _maybe_distil(self, prog: Dict[str, Any]) -> Dict[str, Any] | str:
        full_json = json.dumps(prog)
        if self.n_tokens(full_json, self.model_name) > self.max_prompt_token:
            return self.distill_graph(prog)
        return prog
    
    def distill_graph(prog_dict: Dict[str, Any]) -> Dict[str, Any]:
        if pg is None:
            # Fallback: static metrics only
            return {
                "n_nodes": len(prog_dict.get("nodes", [])),
                "n_edges": len(prog_dict.get("edges", [])),
                "note": "programl not installed, deep metrics skipped",
            }

        g = _safe_program_graph(prog_dict)

        n_instr = sum(1 for _, d in g.nodes(data=True) if d.get("type") == "instruction")
        n_funcs = sum(1 for _, d in g.nodes(data=True) if d.get("type") == "function")

        summary = {
            "n_nodes": g.number_of_nodes(),
            "n_edges": g.number_of_edges(),
            "n_instructions": n_instr,
            "n_functions": n_funcs,
        }
        summary.update(extract_loop_info(g))
        summary.update(summarise_mem(g))
        return summary

    def generate_prompt(
        self,
        programl_graph: Dict[str, Any],
        machine_info: Dict[str, Any],
        config_space: Dict[str, List[Any]],
        attempt_idx: int = 0,
        previous_feedback: str | None = None,
    ) -> str:
        graph_payload = self._maybe_distil(programl_graph)
        if isinstance(graph_payload, dict):
            graph_section = f"### Programl Summary\n{json.dumps(graph_payload, indent=2)}\n\n"
        else:
            graph_section = f"### Programl Graph (raw)\n{json.dumps(graph_payload, indent=2)[:12000]}\n\n"

        system_msg = (
            "You are an HPC optimisation expert. Craft a complete prompt for a Seed‑Picker agent that will choose OpenMP "
            "parameters. Include (1) kernel summary, (2) hardware details, (3) entire configuration search space, "
            "(4) optimisation objective, (5) required JSON schema. If feedback exists, refine to avoid previous mistakes."
        )

        messages = [{"role": "system", "content": system_msg}]

        user_content = (
            graph_section +
            f"### Machine Info\n{json.dumps(machine_info, indent=2)}\n\n" +
            f"### Configuration Space\n{json.dumps(config_space, indent=2)}\n\n"
        )
        if previous_feedback:
            user_content += f"### Feedback\n{previous_feedback}\n\n"
        user_content += "Write the Seed‑Picker prompt now."

        messages.append({"role": "user", "content": user_content})
        return call_openrouter(self.model_name, messages)