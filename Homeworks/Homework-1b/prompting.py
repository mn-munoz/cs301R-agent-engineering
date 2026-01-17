from openai import Client
import argparse
from pathlib import Path
import sys

def main():
    pass

if __name__ == "__main__":
    # Assuming two arguments: One prompt, one input file
    # Assuming prompt file and input file are found in the same directory as this script
    parser = argparse.ArgumentParser('AI Response')
    parser.add_argument('prompt_file', type=Path)
    parser.add_argument('input_file', type=Path)
    parser.add_argument('--model', default='gpt-5-nano')
    args = parser.parse_args()
    
    current_dir = Path(__file__).resolve().parent
    prompt_path = current_dir / args.prompt_file
    input_path = current_dir / args.input_file
    
    print(prompt_path.read_text())
    print(input_path.read_text())
    
    main()