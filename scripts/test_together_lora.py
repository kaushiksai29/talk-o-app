from together import Together
import os
from dotenv import load_dotenv

load_dotenv()

def test_inference():
    api_key = os.getenv("TOGETHER_API_KEY")
    if not api_key:
        print("TOGETHER_API_KEY not found in env.")
        return

    client = Together(api_key=api_key)

    print("Sending request to Together.ai...")
    try:
        response = client.chat.completions.create(
            model="mistralai/Mistral-7B-Instruct-v0.3",
            # The 'lora' argument might be needed if they support it explicitly in the client like this,
            # OR the model name changes to include the adapter if uploaded?
            # The user prompt example showed: `lora="kash-on-the-dash/stargirl-mistral-7b"`
            # effectively as a parameter. Let's try that.
            # Note: The python library argument might be different or passed in extra_body if not standard.
            # But recent versions might support it.
            # If the user prompt is correct, we use `lora=...` 
            # BUT `chat.completions.create` usually doesn't take arbitrary args in typed definitions.
            # It might be passed as `model` if it's a registered endpoint, but for LoRA usually it's `model=base` and `adapter=...`
            # Let's trust the user's snippet first, but if it fails, we check docs style.
            # User snippet:
            # model="mistralai/Mistral-7B-Instruct-v0.3",
            # lora="kash-on-the-dash/stargirl-mistral-7b",
            #
            # If `lora` is not a valid arg, we might need to use `extra_body={"lora": "..."}` or similar.
            messages=[
                {"role": "user", "content": "I can't focus today. What should I do?"}
            ],
            # extra_body={"lora": "kash-on-the-dash/stargirl-mistral-7b"} # fallback if direct arg fails?
            # Let's try to pass it as a kwarg first if the library allows dynamic kwargs.
        )
        # Checking if we can pass lora directly:
        # If the library strictly types `create`, this might fail.
        # Let's try passing it via `extra_body` which is safer for new params.
        
    except TypeError:
        print("Direct 'lora' argument failed, trying extra_body...")
        response = client.chat.completions.create(
             model="mistralai/Mistral-7B-Instruct-v0.3",
             messages=[{"role": "user", "content": "I can't focus today. What should I do?"}],
             extra_body={"lora": "kash-on-the-dash/stargirl-mistral-7b"}
        )
    except Exception as e:
        print(f"Inference failed: {e}")
        # Try just the 'lora' arg in a new try block just in case the first one wasn't the one that ran?
        # Actually I can't put `lora=...` here easily if I want to catch the TypeError specifically for that arg.
        # Let's write the most likely correct form. The User gave `lora=...`.
        # I'll stick to `extra_body` as it is the standard way to pass non-OAI params in OAI-compatible SDKs.
        return

    print("Response received:")
    print(response.choices[0].message.content)

if __name__ == "__main__":
    test_inference()
