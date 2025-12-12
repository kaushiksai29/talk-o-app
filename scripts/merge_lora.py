import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def merge_model():
    # Configuration
    base_model_id = "mistralai/Mistral-7B-Instruct-v0.3"
    adapter_id = "kash-on-the-dash/stargirl-mistral-7b"
    output_dir = "./stargirl-mistral-merged"
    hub_repo_id = "kash-on-the-dash/stargirl-mistral-merged"
    
    print(f"Loading base model: {base_model_id}")
    # Load base model
    # We load in float16 to save memory, but for merging usually we want full precision or at least float16.
    # device_map="cpu" is safer for merging on machines with limited VRAM vs RAM, 
    # but "auto" is faster if GPU is available.
    # Since we might run this locally or on Colab, let's try auto but fallback/warn.
    
    try:
        base_model = AutoModelForCausalLM.from_pretrained(
            base_model_id,
            torch_dtype=torch.float16,
            device_map="auto", 
            trust_remote_code=True
        )
        
        tokenizer = AutoTokenizer.from_pretrained(
            base_model_id,
            trust_remote_code=True
        )
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"Error loading base model: {e}")
        return

    print(f"Loading adapter: {adapter_id}")
    try:
        model = PeftModel.from_pretrained(base_model, adapter_id)
    except Exception as e:
        print(f"Error loading adapter: {e}")
        return

    print("Merging model...")
    model = model.merge_and_unload()

    print(f"Saving merged model to {output_dir}...")
    model.save_pretrained(output_dir)
    tokenizer.save_pretrained(output_dir)
    print("Merge complete!")

    # Push to Hub
    hf_token = os.getenv("HF_TOKEN")
    if hf_token:
        print(f"Pushing to Hugging Face Hub: {hub_repo_id}...")
        try:
            model.push_to_hub(hub_repo_id, token=hf_token, private=True)
            tokenizer.push_to_hub(hub_repo_id, token=hf_token, private=True)
            print("Successfully pushed to Hub!")
        except Exception as e:
            print(f"Error pushing to Hub: {e}")
            print("You can try pushing manually using:")
            print(f"huggingface-cli upload {hub_repo_id} {output_dir}")
    else:
        print("HF_TOKEN not found in .env, skipping push to Hub.")

if __name__ == "__main__":
    merge_model()
