from handler import EndpointHandler
import os

# Ensure we are in the right directory or path setup if needed, 
# although we will likely run this from the parent dir as `python hf_handler/test_handler_local.py`

def test_handler():
    print("Initializing EndpointHandler...")
    # Initialize handler with the model path. 
    # In a real HF endpoint, path is usually "" or the model dir.
    # We use the model name directly if we don't have local weights, 
    # but the tutorial implies we can pass the model name string if local weights aren't strictly required for the init to work,
    # OR we need the model files to be present.
    # The tutorial says: `my_handler = EndpointHandler(path=".")` but they also did `git clone`.
    # Let's try passing the model ID string directly to pipeline if path is "." and it fails, 
    # but the code in handler.py uses `model=path`. 
    # So we should probably pass the model ID "philschmid/distilbert-base-uncased-emotion" 
    # if we want to avoid cloning GBs of data just for a quick test, 
    # OR we rely on `pipeline` downloading it.
    
    # Ideally, we pass the model name.
    model_path = "philschmid/distilbert-base-uncased-emotion"
    
    try:
        my_handler = EndpointHandler(path=model_path)
    except Exception as e:
        print(f"Failed to initialize handler with model path '{model_path}': {e}")
        return

    # prepare sample payloads
    non_holiday_payload = {"inputs": "I am quite excited how this will turn out", "date": "2022-08-08"}
    holiday_payload = {"inputs": "Today is a tough day", "date": "2022-07-04"} # July 4th is US holiday

    print("\nTesting Non-Holiday Payload...")
    non_holiday_pred = my_handler(non_holiday_payload)
    print("Result:", non_holiday_pred)

    print("\nTesting Holiday Payload...")
    holiday_pred = my_handler(holiday_payload)
    print("Result:", holiday_pred)

    # Simple assertions
    # Holiday prediction should be happy/score 1
    if isinstance(holiday_pred, list) and len(holiday_pred) > 0:
        if holiday_pred[0].get("label") == "happy":
            print("\nSUCCESS: Holiday logic works!")
        else:
            print("\nFAILURE: Holiday logic did not return 'happy'.")
    else:
        print("\nFAILURE: Unexpected holiday prediction format.")

if __name__ == "__main__":
    test_handler()
