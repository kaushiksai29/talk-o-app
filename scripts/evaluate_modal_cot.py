
import os
import json
import random
import requests
import time
from dotenv import load_dotenv

env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env")
load_dotenv(env_path)

MODAL_URL = os.getenv("MODAL_API_URL")
if not MODAL_URL:
    print(f"Error: MODAL_API_URL not found in {env_path}")
    # Fallback to hardcoded check if env fail (debug)
    with open(env_path, 'r') as f:
        print("Env content preview:", f.read()[:50])
    exit(1)

COT_FILE = "cot/stargirl_explicit_cot.jsonl"

def load_cot_data(filepath):
    data = []
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                data.append(json.loads(line))
    return data

def call_modal(prompt):
    try:
        payload = {
            "prompt": prompt,
            "max_tokens": 300,
            "temperature": 0.7
        }
        response = requests.post(
            MODAL_URL, 
            json=payload, 
            headers={"Content-Type": "application/json"},
            timeout=180
        )
        response.raise_for_status()
        return response.json().get("text", "")
    except Exception as e:
        return f"Error: {e}"

def format_few_shot_prompt(target_input, examples):
    # Construct a prompt that shows Input -> Thought -> Output
    prompt = "<s>[INST] You are Stargirl. Answer the user's input with empathy and clear reasoning.\n\n"
    
    for ex in examples:
        prompt += f"User: {ex['input']}\n"
        prompt += f"Thought: {ex['thought']}\n"
        prompt += f"Stargirl: {ex['output']}\n\n"
        
    prompt += f"User: {target_input}\n"
    prompt += "Thought: [/INST]" 
    # Ending with "Thought:" invites the model to continue with the reasoning step.
    return prompt

def main():
    print("Loading CoT dataset...")
    data = load_cot_data(COT_FILE)
    
    # Select test cases (last 5 to avoid overlap with few-shot examples if we picked first 3)
    test_cases = data[-5:] 
    
    # Select few-shot examples (first 3)
    few_shot_examples = data[:3]
    
    results = []
    
    print(f"Running evaluation on {len(test_cases)} cases...")
    
    for i, case in enumerate(test_cases):
        print(f"Test {i+1}/{len(test_cases)}: {case['input'][:50]}...")
        
        prompt = format_few_shot_prompt(case['input'], few_shot_examples)
        
        start_time = time.time()
        model_response = call_modal(prompt)
        duration = time.time() - start_time
        
        result_entry = {
            "input": case['input'],
            "expected_thought": case['thought'],
            "expected_output": case['output'],
            "generated_response": model_response,
            "duration": duration
        }
        results.append(result_entry)
        print(f"  -> Response received ({duration:.2f}s)\n")

    # Save to Markdown
    with open("cot_evaluation_results.md", "w", encoding="utf-8") as f:
        f.write("# CoT Evaluation Results (Modal)\n\n")
        f.write(f"**Date**: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"**Model URL**: `{MODAL_URL}`\n")
        f.write(f"**Strategy**: Few-Shot CoT (3 examples)\n\n")
        
        for i, res in enumerate(results):
            f.write(f"## Test Case {i+1}\n")
            f.write(f"**Input**: {res['input']}\n\n")
            f.write(f"**Expected Thought**: *{res['expected_thought']}*\n")
            f.write(f"**Expected Output**: {res['expected_output']}\n\n")
            f.write(f"### Model Generation\n")
            f.write(f"```\n{res['generated_response']}\n```\n")
            f.write(f"*Time taken: {res['duration']:.2f}s*\n\n")
            f.write("---\n")
            
    print("Evaluation complete. Results saved to cot_evaluation_results.md")

if __name__ == "__main__":
    main()
