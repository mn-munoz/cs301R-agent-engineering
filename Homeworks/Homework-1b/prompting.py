from time import time
from openai import Client
import argparse
from pathlib import Path
from usage import print_usage
import json

def main(model: str, prompt: str, text: str):
    client = Client()
    prompt += text
    
    start = time()
    response = client.responses.create(
        model=model,
        input=prompt,
        # reasoning={'effort': 'low'}
    )
    print(response.output_text)

    print(f'{round(time()-start, 2)} seconds elapsed')
    print_usage(model, response.usage)
    
    

if __name__ == "__main__":
    # Assuming two arguments: One prompt, one input file
    # Assuming prompt file and input file are found in the same directory as this script
    parser = argparse.ArgumentParser('AI Response')
    parser.add_argument('prompt_file', type=Path)
    parser.add_argument('input_file', type=Path)
    parser.add_argument('--model', default='gpt-5-nano')
    args = parser.parse_args()
    
    current_dir = Path(__file__).resolve().parent
    args.prompt_file = current_dir / args.prompt_file
    args.input_file = current_dir / args.input_file

    main(args.model, args.prompt_file.read_text(), args.input_file.read_text())