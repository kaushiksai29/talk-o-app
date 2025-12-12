
import os
import modal

# --- CONFIGURATION ---
# NEW FILE: modal_deploy_v2.py
# Using Transformers + PEFT (No vLLM)
MODEL_ID = "kash-on-the-dash/stargirl-mistral-7b"
ADAPTER_DIR = "/model/adapter"
BASE_MODEL_DIR = "/model/base"

def download_model():
    import os
    import json
    from huggingface_hub import snapshot_download
    
    token = os.environ.get("HF_TOKEN")
    if not token:
        print("WARNING: HF_TOKEN not found!")

    # 1. Download Adapter
    print(f"Downloading Adapter {MODEL_ID} to {ADAPTER_DIR}...")
    snapshot_download(
        repo_id=MODEL_ID,
        token=token,
        local_dir=ADAPTER_DIR,
        ignore_patterns=["*.pt", "*.bin"]
    )
    
    # 2. Identify Base Model
    # Explicitly using v0.3 per previous request
    base_model_id = "mistralai/Mistral-7B-Instruct-v0.3"
    print(f"Using Base Model: {base_model_id}")
    
    # 3. Download Base Model
    print(f"Downloading Base Model {base_model_id} to {BASE_MODEL_DIR}...")
    snapshot_download(
        repo_id=base_model_id,
        token=token,
        local_dir=BASE_MODEL_DIR,
        ignore_patterns=["*.pt", "*.bin"]
    )

IMAGE = (
    modal.Image.from_registry("nvidia/cuda:12.1.1-devel-ubuntu22.04", add_python="3.10")
    .apt_install("git", "build-essential", "rustc", "cargo")
    .run_commands("python -m pip install --upgrade pip")
    .pip_install(
        "torch>=2.1.0",
        "transformers>=4.40.0", 
        "peft>=0.10.0",
        "accelerate>=0.29.0",
        "huggingface_hub[cli]>=0.23.0",
        "bitsandbytes",
        "fastapi",
        "pydantic"
    )
    .run_function(
        download_model,
        secrets=[modal.Secret.from_name("huggingface-secret")]
    )
)

app = modal.App("stargirl-inference-v2")

@app.cls(
    gpu="A10G",
    image=IMAGE,
    secrets=[modal.Secret.from_name("huggingface-secret")],
    timeout=600,
    scaledown_window=300, 
)
class StargirlModel:
    @modal.enter()
    def load_model(self):
        import torch
        from transformers import AutoModelForCausalLM, AutoTokenizer
        from peft import PeftModel
        
        print("Loading Tokenizer...")
        self.tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL_DIR)
        
        print(f"Loading Base Model from {BASE_MODEL_DIR}...")
        base_model = AutoModelForCausalLM.from_pretrained(
            BASE_MODEL_DIR,
            torch_dtype=torch.float16,
            device_map="auto"
        )
        
        print(f"Loading LoRA Adapter from {ADAPTER_DIR}...")
        self.model = PeftModel.from_pretrained(
            base_model,
            ADAPTER_DIR
        )
        print("Model loaded successfully!")

    @modal.fastapi_endpoint(method="POST")
    def generate(self, data: dict):
        import torch
        
        prompt = data.get("prompt", "")
        if not prompt:
            return {"error": "Prompt is required"}
            
        inputs = self.tokenizer(prompt, return_tensors="pt").to("cuda")
        
        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=data.get("max_tokens", 200),
                temperature=data.get("temperature", 0.7),
                do_sample=True,
                pad_token_id=self.tokenizer.eos_token_id
            )
            
        generated_text = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        # Strip prompt to perform like vLLM text generation
        prompt_len = len(self.tokenizer.decode(inputs.input_ids[0], skip_special_tokens=True))
        new_text = generated_text[len(prompt):] 
        # Safer stripping by token count or just string matching if exact
        if generated_text.startswith(prompt):
             new_text = generated_text[len(prompt):]
        else:
             # Fallback if whitespace diffs
             new_text = generated_text

        return {"text": new_text}
