import json
import random
import os

# Paths
cot_path = r"c:\Users\kaush\Downloads\talk-o-app\cot\stargirl_cot_dataset_grok.jsonl"
whatsapp_path = r"c:\Users\kaush\Downloads\talk-o-app\cot\stargirl_whatsapp_qlora_fixed.jsonl"
voice_path = r"c:\Users\kaush\Downloads\talk-o-app\cot\stargirl_voice_training.jsonl"
output_path = r"c:\Users\kaush\Downloads\talk-o-app\cot\stargirl_combined_training.jsonl"

# System Prompt
SYSTEM_PROMPT = "You are Stargirl, a warm and emotionally intelligent AI companion designed specifically for people with ADHD. You speak like a close friend - casual, supportive, and real. You don't lecture or give generic advice. You listen, you understand, and you respond with genuine care. Your tone is conversational, sometimes playful, always authentic."

combined_data = []
seen_entries = set()

def add_entry(entry):
    # Normalize to string for deduplication
    entry_str = json.dumps(entry, sort_keys=True)
    if entry_str not in seen_entries:
        seen_entries.add(entry_str)
        combined_data.append(entry)
        return True
    return False

# 1. Process CoT Data
print(f"Processing CoT data from {cot_path}...")
try:
    with open(cot_path, 'r', encoding='utf-8') as f:
        for line in f:
            if not line.strip(): continue
            entry = json.loads(line)
            
            # Extract fields
            user_input = entry.get('input', '')
            thought = entry.get('thought', '')
            output = entry.get('output', '')
            
            if not user_input or not output:
                continue

            # Format with <thought> block
            if thought:
                assistant_response = f"<thought>{thought}</thought>\n{output}"
            else:
                assistant_response = output

            # Create conversation object
            conversation_entry = {
                "conversations": [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_input},
                    {"role": "assistant", "content": assistant_response}
                ]
            }
            add_entry(conversation_entry)
    print(f"Added {len(combined_data)} CoT examples.")

except Exception as e:
    print(f"Error processing CoT data: {e}")

# 2. Process Voice Data (New)
print(f"Processing Voice data from {voice_path}...")
try:
    if os.path.exists(voice_path):
        with open(voice_path, 'r', encoding='utf-8') as f:
            voice_count = 0
            for line in f:
                if not line.strip(): continue
                entry = json.loads(line)
                
                user_input = entry.get('input', '')
                thought = entry.get('thought', '')
                output = entry.get('output', '')
                
                if not user_input or not output:
                    continue

                if thought:
                    assistant_response = f"<thought>{thought}</thought>\n{output}"
                else:
                    assistant_response = output

                conversation_entry = {
                    "conversations": [
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": user_input},
                        {"role": "assistant", "content": assistant_response}
                    ]
                }
                add_entry(conversation_entry)
                voice_count += 1
        print(f"Added {voice_count} Voice examples.")
    else:
        print(f"Voice data file not found at {voice_path} (skipping)")

except Exception as e:
    print(f"Error processing Voice data: {e}")

# 2. Process WhatsApp Data
print(f"Processing WhatsApp data from {whatsapp_path}...")
whatsapp_count = 0
try:
    with open(whatsapp_path, 'r', encoding='utf-8') as f:
        for line in f:
            if not line.strip(): continue
            entry = json.loads(line)
            
            # Check structure
            if "conversations" in entry:
                # Ensure system prompt is consistent (optional, but good for consistency)
                # We can either keep the original or replace it. 
                # The original seems to match our target, so we'll keep it but ensure structure.
                
                # Check if system prompt is in "system" field or inside conversations
                msgs = entry["conversations"]
                
                # If "system" field exists at top level, convert to conversation message if needed
                # Unsloth/ShareGPT often expects system as the first message or a separate field depending on loader.
                # We will standardize to: [{"role": "system", ...}, {"role": "user", ...}, ...]
                
                new_msgs = []
                
                # Add system prompt if not present
                if msgs and msgs[0]['role'] != 'system':
                     # Use the file's system prompt if available, else default
                    sys_content = entry.get("system", SYSTEM_PROMPT)
                    new_msgs.append({"role": "system", "content": sys_content})
                
                new_msgs.extend(msgs)
                
                add_entry({"conversations": new_msgs})
                whatsapp_count += 1
            else:
                # Handle other formats if any?
                pass
    print(f"Added {whatsapp_count} WhatsApp examples.")

except Exception as e:
    print(f"Error processing WhatsApp data: {e}")

# 3. Shuffle and Save
random.shuffle(combined_data)

print(f"Saving {len(combined_data)} total examples to {output_path}...")
with open(output_path, 'w', encoding='utf-8') as f:
    for entry in combined_data:
        f.write(json.dumps(entry) + '\n')

print("Done!")
