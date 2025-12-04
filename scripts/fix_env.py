
import os

file_path = '.env'

with open(file_path, 'r') as f:
    content = f.read()

# Naive parsing to handle the weird whitespace I saw
# I'll try to extract the key by finding "SUPABASE_KEY=" and taking everything until the next key or EOF
# But simpler: just read lines and clean them up.

lines = content.splitlines()
cleaned_lines = []
supabase_url = ""
supabase_key = ""

current_key = None
current_value = []

for line in lines:
    line = line.strip()
    if not line:
        continue
    
    if "=" in line:
        # New key
        if current_key:
            # Save previous
            full_val = "".join(current_value)
            cleaned_lines.append(f"{current_key}={full_val}")
            if current_key == "SUPABASE_URL": supabase_url = full_val
            if current_key == "SUPABASE_KEY": supabase_key = full_val
        
        parts = line.split("=", 1)
        current_key = parts[0].strip()
        current_value = [parts[1].strip()]
    else:
        # Continuation of previous key (if it was split by newlines)
        if current_key:
            current_value.append(line.strip())

# Save last one
if current_key:
    full_val = "".join(current_value)
    cleaned_lines.append(f"{current_key}={full_val}")
    if current_key == "SUPABASE_URL": supabase_url = full_val
    if current_key == "SUPABASE_KEY": supabase_key = full_val

# Add NEXT_PUBLIC vars
if supabase_url:
    cleaned_lines.append(f"NEXT_PUBLIC_SUPABASE_URL={supabase_url}")
if supabase_key:
    cleaned_lines.append(f"NEXT_PUBLIC_SUPABASE_ANON_KEY={supabase_key}")

with open(file_path, 'w') as f:
    f.write('\n'.join(cleaned_lines))

print("Fixed .env file.")
print(f"URL: {supabase_url}")
print(f"Key: {supabase_key[:10]}...{supabase_key[-10:]}")
