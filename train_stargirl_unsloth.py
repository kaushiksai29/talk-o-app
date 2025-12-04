"""
Stargirl QLoRA Fine-Tuning Script
=================================
Using Unsloth for efficient fine-tuning on consumer GPUs.

Requirements:
- Google Colab Pro (A100) or RunPod (RTX 4090 / A100)
- ~8GB VRAM minimum for 3B model
- ~16GB VRAM for 8B model

Install dependencies:
pip install unsloth
pip install --no-deps trl peft accelerate bitsandbytes
"""

from unsloth import FastLanguageModel
import torch
from trl import SFTTrainer
from transformers import TrainingArguments
from datasets import load_dataset
import json

# ============================================
# Configuration
# ============================================

MODEL_NAME = "unsloth/Llama-3.2-3B-Instruct"  # Fast and efficient
# MODEL_NAME = "unsloth/Meta-Llama-3.1-8B-Instruct"  # More capable, needs more VRAM

MAX_SEQ_LENGTH = 2048
LOAD_IN_4BIT = True

LORA_R = 16
LORA_ALPHA = 32
LORA_DROPOUT = 0.05

# Training
BATCH_SIZE = 2
GRADIENT_ACCUMULATION = 4
LEARNING_RATE = 2e-4
MAX_STEPS = 500
WARMUP_STEPS = 10

# ============================================
# Load Model
# ============================================

print("Loading model...")
model, tokenizer = FastLanguageModel.from_pretrained(
    model_name=MODEL_NAME,
    max_seq_length=MAX_SEQ_LENGTH,
    dtype=None,  # Auto-detect
    load_in_4bit=LOAD_IN_4BIT,
)

# ============================================
# Apply LoRA
# ============================================

print("Applying LoRA adapters...")
model = FastLanguageModel.get_peft_model(
    model,
    r=LORA_R,
    target_modules=[
        "q_proj", "k_proj", "v_proj", "o_proj",
        "gate_proj", "up_proj", "down_proj",
    ],
    lora_alpha=LORA_ALPHA,
    lora_dropout=LORA_DROPOUT,
    bias="none",
    use_gradient_checkpointing="unsloth",
    random_state=42,
)

# ============================================
# Prepare Dataset
# ============================================

print("Loading dataset...")

# Load your JSONL data
def load_jsonl(filepath):
    data = []
    with open(filepath, 'r') as f:
        for line in f:
            data.append(json.loads(line))
    return data

training_data = load_jsonl("stargirl_qlora.jsonl")

# Format for training
def format_prompt(example):
    """Format conversation for training."""
    system = example.get('system', '')
    conversations = example.get('conversations', [])
    
    # Build prompt
    prompt = f"<|begin_of_text|><|start_header_id|>system<|end_header_id|>\n\n{system}<|eot_id|>"
    
    for conv in conversations:
        role = conv['role']
        content = conv['content']
        if role == 'user':
            prompt += f"<|start_header_id|>user<|end_header_id|>\n\n{content}<|eot_id|>"
        else:
            prompt += f"<|start_header_id|>assistant<|end_header_id|>\n\n{content}<|eot_id|>"
    
    return {"text": prompt}

# Convert to HuggingFace dataset
from datasets import Dataset
formatted_data = [format_prompt(d) for d in training_data]
dataset = Dataset.from_list(formatted_data)

print(f"Dataset size: {len(dataset)} examples")

# ============================================
# Training
# ============================================

print("Starting training...")

trainer = SFTTrainer(
    model=model,
    tokenizer=tokenizer,
    train_dataset=dataset,
    dataset_text_field="text",
    max_seq_length=MAX_SEQ_LENGTH,
    dataset_num_proc=2,
    packing=False,
    args=TrainingArguments(
        per_device_train_batch_size=BATCH_SIZE,
        gradient_accumulation_steps=GRADIENT_ACCUMULATION,
        warmup_steps=WARMUP_STEPS,
        max_steps=MAX_STEPS,
        learning_rate=LEARNING_RATE,
        fp16=not torch.cuda.is_bf16_supported(),
        bf16=torch.cuda.is_bf16_supported(),
        logging_steps=10,
        optim="adamw_8bit",
        weight_decay=0.01,
        lr_scheduler_type="linear",
        seed=42,
        output_dir="stargirl-lora",
        save_steps=100,
    ),
)

# Train
trainer_stats = trainer.train()

# ============================================
# Save Model
# ============================================

print("Saving LoRA adapter...")
model.save_pretrained("stargirl-lora")
tokenizer.save_pretrained("stargirl-lora")

# ============================================
# Test Generation
# ============================================

print("\n" + "="*50)
print("Testing Stargirl...")
print("="*50)

FastLanguageModel.for_inference(model)

test_prompts = [
    "I can't focus on anything today and I feel like a failure",
    "I've been so anxious about this job interview tomorrow",
    "My friend is ignoring me and I don't know what I did wrong",
]

for prompt in test_prompts:
    messages = [
        {"role": "system", "content": "You are Stargirl, a warm and emotionally intelligent AI companion designed specifically for people with ADHD. You speak like a close friend - casual, supportive, and real."},
        {"role": "user", "content": prompt}
    ]
    
    inputs = tokenizer.apply_chat_template(
        messages,
        tokenize=True,
        add_generation_prompt=True,
        return_tensors="pt",
    ).to("cuda")
    
    outputs = model.generate(
        input_ids=inputs,
        max_new_tokens=128,
        use_cache=True,
        temperature=0.7,
    )
    
    response = tokenizer.decode(outputs[0], skip_special_tokens=True)
    print(f"\nUser: {prompt}")
    print(f"Stargirl: {response.split('assistant')[-1].strip()}")

print("\n✅ Training complete! LoRA adapter saved to 'stargirl-lora/'")
print("\nNext steps:")
print("1. Merge LoRA with base model for deployment")
print("2. Export to GGUF for llama.cpp")
print("3. Or use directly with HuggingFace transformers")
