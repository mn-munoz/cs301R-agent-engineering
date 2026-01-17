from openai import Client
from time import time
from usage import print_usage

def print_result(model, response, start_time):
    print("Response Output:")
    print(response.output_text)
    
    print(f"This response took {round(time() - start_time, 2)} seconds.")
    print_usage(model, response.usage)

def main():
    client = Client()
    start_time = time()
    model = "gpt-5-nano"
    
    response = client.responses.create(
        model=model,
        input="Write a fancy greeting message using shakespearean English.",
        reasoning={"effort": "low"}
    )
    
    print_result(model, response, start_time)
    

if __name__ == "__main__":
    main()