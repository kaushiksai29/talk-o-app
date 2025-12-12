
import sys
import os

# Add temp_lib to path
sys.path.append(os.path.abspath("./temp_lib"))

from together.cli.cli import main

def check_help():
    print("--- HELP: together models upload ---\n")
    try:
        main(args=["models", "upload", "--help"], standalone_mode=False)
    except SystemExit:
        pass

if __name__ == "__main__":
    check_help()
