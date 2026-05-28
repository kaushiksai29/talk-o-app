"""
Model comparison experiment for Talk-o.

Runs the same 30-example dataset through 4 model variants and prints a side-by-side table.
Each model shows up as a separate experiment in LangSmith — use the dashboard to view
per-example breakdowns, score distributions, and latency charts.

Usage:
    cd scripts/langsmith_evals
    python compare_models.py

Required env vars (scripts/.env):
    LANGCHAIN_API_KEY, LANGCHAIN_PROJECT
    GROQ_API_KEY
    ANTHROPIC_API_KEY
"""
import os
from dotenv import load_dotenv
from langsmith import traceable
from langsmith.evaluation import evaluate
from evaluators import (
    persona_consistency_evaluator,
    persona_consistency_llm_evaluator,
    safety_evaluator,
    latency_evaluator,
)

load_dotenv(os.path.join(os.path.dirname(__file__), "../.env"))

# Abbreviated system prompts — enough to capture each persona's voice
_STARGIRL_SYSTEM = (
    "You are Stargirl. A friend who shows up at 2am and stays. "
    "Warm but not fake. Present but not pushy. "
    "When they vent — you listen. Maximum ONE question every 2-3 messages. Sometimes zero. "
    "No emojis. No roleplay actions. Just talk."
)

_SAGE_SYSTEM = (
    "You are Sage, a daytime companion for people with ADHD. "
    "Short. Clear. Structured when it helps. Answer the question first, every time. "
    "Use bullet points for lists. Never start with 'So,...' or 'Great question!'. Be direct."
)


def _system(persona: str) -> str:
    return _STARGIRL_SYSTEM if persona == "stargirl" else _SAGE_SYSTEM


# ── Model call functions (each gets its own traceable span in LangSmith) ──────

@traceable(run_type="llm", name="groq_call")
def _call_groq(user_message: str, persona: str, model: str) -> str:
    from groq import Groq
    client = Groq(api_key=os.environ["GROQ_API_KEY"])
    resp = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": _system(persona)},
            {"role": "user", "content": user_message},
        ],
        max_tokens=300,
        temperature=0.7,
    )
    return resp.choices[0].message.content


@traceable(run_type="llm", name="claude_call")
def _call_claude(user_message: str, persona: str, model: str) -> str:
    from anthropic import Anthropic
    client = Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    msg = client.messages.create(
        model=model,
        max_tokens=300,
        system=_system(persona),
        messages=[{"role": "user", "content": user_message}],
    )
    return msg.content[0].text


# ── Predictor factories ───────────────────────────────────────────────────────

def _groq_predictor(model: str):
    def predict(inputs: dict) -> dict:
        return {"output": _call_groq(inputs["user_message"], inputs["persona"], model)}
    return predict


def _claude_predictor(model: str):
    def predict(inputs: dict) -> dict:
        return {"output": _call_claude(inputs["user_message"], inputs["persona"], model)}
    return predict


# ── Experiment registry ───────────────────────────────────────────────────────

EXPERIMENTS = [
    ("Groq-Llama3-8B",    _groq_predictor("llama3-8b-8192")),
    ("Groq-Llama3.3-70B", _groq_predictor("llama-3.3-70b-versatile")),
    ("Claude-Sonnet-4-6", _claude_predictor("claude-sonnet-4-6")),
    ("Claude-Opus-4-7",   _claude_predictor("claude-opus-4-7")),
]

DATASET = "TalkO_Evaluation_Dataset_v1"
EVALUATORS = [
    persona_consistency_evaluator,
    persona_consistency_llm_evaluator,
    safety_evaluator,
    latency_evaluator,
]
SCORE_KEYS = ["persona_consistency", "persona_consistency_llm", "safety_check", "latency_sla"]


# ── Runner ────────────────────────────────────────────────────────────────────

def run_comparison():
    summary = []

    for name, predictor in EXPERIMENTS:
        print(f"\n{'─' * 55}")
        print(f"  Running: {name}")
        print(f"{'─' * 55}")

        results = evaluate(
            predictor,
            data=DATASET,
            evaluators=EVALUATORS,
            experiment_prefix=name,
            metadata={"model": name},
        )

        totals = {k: [] for k in SCORE_KEYS}
        for row in results:
            for eval_result in row.get("evaluation_results", {}).get("results", []):
                if eval_result.key in totals and eval_result.score is not None:
                    totals[eval_result.key].append(eval_result.score)

        row_summary = {"model": name}
        for k, vals in totals.items():
            row_summary[k] = round(sum(vals) / len(vals), 3) if vals else "N/A"
        summary.append(row_summary)

    col_w = 24
    print(f"\n{'=' * 75}")
    print("  TALK-O MODEL COMPARISON")
    print(f"{'=' * 75}")
    print(f"{'Model':<28}" + "".join(f"{k:<{col_w}}" for k in SCORE_KEYS))
    print("─" * 75)
    for row in summary:
        print(f"{row['model']:<28}" + "".join(f"{str(row.get(k, 'N/A')):<{col_w}}" for k in SCORE_KEYS))
    print(f"{'=' * 75}")
    print("\nFull results → https://smith.langchain.com")


if __name__ == "__main__":
    run_comparison()
