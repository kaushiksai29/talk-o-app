import os

def clean_env(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        new_lines = []
        groq_key = "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"
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Check for corrupted Groq line
            if "GROQ_API_KEY" in line:
                continue # Skip existing bad lines
            
            new_lines.append(line)
        
        # Add correct Groq key
        new_lines.append(f"GROQ_API_KEY={groq_key}")
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write('\n'.join(new_lines))
            
        print(f"Cleaned {filepath}")
        
    except Exception as e:
        print(f"Error cleaning {filepath}: {e}")

clean_env('.env')
clean_env('scripts/.env')
