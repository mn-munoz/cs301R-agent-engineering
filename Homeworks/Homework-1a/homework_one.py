from openai import Client
from time import time
from usage import print_usage
import argparse
from pathlib import Path
from typing import Optional

def print_result(model, response, start_time):
    print("Response Output:")
    print(response.output_text)
    
    print(f"This response took {round(time() - start_time, 2)} seconds.")
    print_usage(model, response.usage)

def main(prompt: str, input: Optional[str] = None):
    client = Client()
    start_time = time()
    model = "gpt-4o-mini"
    prompt += input if input else ""
    
    response = client.responses.create(
        model=model,
        input=prompt,
        # reasoning={"effort": "low"}
    )
    
    print_result(model, response, start_time)
    

if __name__ == "__main__":
    parser = argparse.ArgumentParser('AI Response')
    parser.add_argument('prompt_file', type=Path)
    parser.add_argument('input_file', type=Path, nargs='?', default=None)
    args = parser.parse_args()
    
    current_dir = Path(__file__).resolve().parent
    args.prompt_file = current_dir / args.prompt_file
    if args.input_file is not None:
        args.input_file = current_dir / args.input_file

    main(args.prompt_file.read_text(), args.input_file.read_text() if args.input_file else None)