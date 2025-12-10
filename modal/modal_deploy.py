
import os
import modal

# --- CONFIGURATION ---
MODEL_ID = "kash-on-the-dash/stargirl-mistral-7b"

def download_model():
    from huggingface_hub import snapshot_download
    print(f"Downloading {MODEL_ID}...")
    snapshot_download(MODEL_ID)

# We used a standard CUDA image that works well with vLLM
# We use .run_function to download the model during the image build
IMAGE = (
    modal.Image.from_registry("nvidia/cuda:12.1.1-devel-ubuntu22.04", add_python="3.10")
    .pip_install(
        "vllm==0.6.3",
        "huggingface_hub"
    )
    .run_function(
        download_model,
        secrets=[modal.Secret.from_name("huggingface-secret")]
    )
)

app = modal.App("stargirl-inference")

@app.cls(
    gpu="A10G",  # A10G is cost-effective and powerful enough for 7B models
    image=IMAGE,
    secrets=[modal.Secret.from_name("huggingface-secret")], # Needed for load_model too if vLLM checks auth
    timeout=600,
    container_idle_timeout=300, # Keep container alive for 5 mins to avoid cold starts
)
class StargirlModel:
    @modal.enter()
    def load_model(self):
        # This runs when the container starts
        from vllm import LLM
        print(f"Loading vLLM engine for {MODEL_ID}...")
        self.llm = LLM(model=MODEL_ID)

    @modal.web_endpoint(method="POST")
    def generate(self, data: dict):
        # The API endpoint
        from vllm import SamplingParams
        
        prompt = data.get("prompt", "")
        if not prompt:
            return {"error": "Prompt is required"}

        # Default parameters matching the Stargirl persona (creative but coherent)
        sampling_params = SamplingParams(
            temperature=0.8,
            top_p=0.95,
            max_tokens=data.get("max_tokens", 200),
        )
        
        output_request = self.llm.generate([prompt], sampling_params)
        output_text = output_request[0].outputs[0].text
        
        return {"text": output_text}

# --- INSTRUCTIONS ---
# 1. Install Modal: pip install modal
# 2. Authenticate: modal setup
# 3. Create Secret: modal secret create huggingface-secret HF_TOKEN=your_token_here
# 4. Deploy: modal deploy modal/modal_deploy.py
# 5. Test: curl -X POST https://YOUR_USER--stargirl-inference-stargirlmodel-generate.modal.run -H "Content-Type: application/json" -d '{"prompt": "User: Hi Stargirl, I feel tired.\nStargirl:"}'
