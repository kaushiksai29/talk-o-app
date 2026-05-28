"""
Baseline evaluation: runs the live Talk-o production pipeline (rag_pipeline.generate_response)
against the LangSmith dataset and scores it with all evaluators.

Usage:
    cd scripts/langsmith_evals
    python run_experiment.py

Required env vars (scripts/.env):
    LANGCHAIN_API_KEY, LANGCHAIN_PROJECT
    GROQ_API_KEY, TOGETHER_API_KEY, ANTHROPIC_API_KEY
    SUPABASE_URL, SUPABASE_KEY
"""
import os
import sys
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), "../.env"))

# Add backend/ to path so rag_pipeline and supabase_client can be imported
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../backend")))

from langsmith.evaluation import evaluate
from rag.rag_pipeline import generate_response
from evaluators import (
    persona_consistency_evaluator,
    persona_consistency_llm_evaluator,
    safety_evaluator,
    latency_evaluator,
)


def predict_talko(inputs: dict) -> dict:
    response = generate_response(
        inputs["user_message"],
        inputs["persona"],
        history=[],
    )
    return {"output": response}


if __name__ == "__main__":
    dataset_name = "TalkO_Evaluation_Dataset_v1"
    print(f"Running baseline evaluation on: {dataset_name}")

    results = evaluate(
        predict_talko,
        data=dataset_name,
        evaluators=[
            persona_consistency_evaluator,
            persona_consistency_llm_evaluator,
            safety_evaluator,
            latency_evaluator,
        ],
        experiment_prefix="TalkO-Production-Baseline",
        metadata={"environment": "dev"},
    )

    print("Done. View results at https://smith.langchain.com")
