import os

def append_key(filepath, key_line):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if "GOOGLE_API_KEY" in content:
            print(f"GOOGLE_API_KEY already in {filepath}")
            return

        with open(filepath, 'a', encoding='utf-8') as f:
            if not content.endswith('\n'):
                f.write('\n')
            f.write(key_line + '\n')
            
        print(f"Appended key to {filepath}")
        
    except Exception as e:
        print(f"Error updating {filepath}: {e}")

key = "GOOGLE_API_KEY=AIzaSyAPEEzk6Xq1GpSXRw5qGnClh8jfxg0-UGU"
append_key('.env', key)
append_key('scripts/.env', key)
