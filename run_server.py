
import os
import sys
import uvicorn

if __name__ == "__main__":
    print("--- Starting Backend using run_server.py ---")
    
    # Get the project root directory
    project_root = os.path.dirname(os.path.abspath(__file__))
    backend_dir = os.path.join(project_root, "backend")
    
    # Change to backend directory
    if os.path.exists(backend_dir):
        print(f"Changing working directory to: {backend_dir}")
        os.chdir(backend_dir)
        sys.path.insert(0, backend_dir)
    else:
        print(f"Warning: backend directory not found at {backend_dir}. listing root:")
        print(os.listdir(project_root))
        # Fallback: assume we are already in the right place or struct is different
        
    # Get Port from Environment
    try:
        port = int(os.environ.get("PORT", 8080))
    except ValueError:
        port = 8080
    
    print(f"Binding to PORT: {port}")
    
    # Run Uvicorn
    # Using "main:app" string allows uvicorn to handle the import and reloading
    try:
        uvicorn.run("main:app", host="0.0.0.0", port=port, log_level="info")
    except Exception as e:
        print(f"Failed to start uvicorn: {e}")
        sys.exit(1)
