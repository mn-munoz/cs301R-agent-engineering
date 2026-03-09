from pathlib import Path

import yaml
import json
from typing import TypedDict
from openai import AsyncOpenAI

from tools import ToolBox
from usage import print_usage

toolbox = ToolBox()

class Agent(TypedDict):
    model: str
    prompt: str
    tools: list[str]
    kwargs: dict

async def run_agent(
        client,
        toolbox,
        agent: Agent,
        user_message: str | None = None,
        history: list | None = None,
        usage: list | None = None
) -> str:
    if history is None:
        history = []
    if usage is None:
        usage = []

    if prompt := agent.get('prompt'):
        history.append({'role': 'system', 'content': prompt})
    
    if user_message:
        history.append({'role': 'user', 'content': user_message})
        
    while True:
        response = await client.responses.create(
            input=history,
            model=agent.get('model', 'gpt-5-mini'),
            tools=toolbox.get_tools(agent.get('tools', [])),
            **agent.get('kwargs', {})
        )

        usage.append(response.usage)
        history.extend(
            response.output
        )

        for item in response.output:
            if item.type == 'function_call':
                print(f'{item.name}({item.arguments})')

                func = toolbox.get_tool_function(item.name)
                args = json.loads(item.arguments)
                result = func(**args)
                history.append({
                    'type': 'function_call_output',
                    'call_id': item.call_id,
                    'output': str(result)
                })

            elif item.type == 'message':
                return '\n'.join(chunk.text for chunk in item.content)
            
async def main(agents_config: Path):
    client = AsyncOpenAI()
    
    # Load all agents from config
    with open(agents_config, 'r') as f:
        config = yaml.safe_load(f)
    
    agents = {agent['name']: agent for agent in config['agents']}
    
    usage = []
    
    # Step 1: Generate the murder mystery story
    print("🔍 Creating your murder mystery...")
    story_response = await run_agent(
        client, toolbox, agents['plot-creator'],
        user_message=None, history=None, usage=usage
    )
    
    # Parse the story JSON
    story_data = json.loads(story_response)
    
    # Display the story to the user
    print(f"\n📖 {story_data['title']}")
    print("=" * (len(story_data['title']) + 4))
    print(f"Setting: {story_data['setting']}")
    print(f"\n{story_data['story']}")
    print(f"\nVictim: {story_data['victim']}")
    print("\n" + "="*60)
    
    # Step 2: Generate hints based on the story
    print("\n🕵️ Preparing hints for your investigation...")
    hints_response = await run_agent(
        client, toolbox, agents['hint-generator'],
        user_message=story_response, history=None, usage=usage
    )
    
    # Parse the hints JSON
    hints_data = json.loads(hints_response)
    
    # Step 3: Start interactive chat with mystery assistant
    print("\n🗣️  Starting your investigation with your detective assistant...")
    print("Type 'quit' to exit at any time.\n")
    
    # Prepare initial context for the assistant
    initial_context = f"""Here is the murder mystery case and available hints:

CASE: {json.dumps(story_data, indent=2)}

AVAILABLE HINTS: {json.dumps(hints_data, indent=2)}

Present this mystery to the user and help them solve it step by step."""
    
    # Initialize chat history for the assistant
    chat_history = []
    
    # First interaction - assistant presents the case
    response = await run_agent(
        client, toolbox, agents['mystery-assistant'],
        user_message=initial_context, history=chat_history, usage=usage
    )
    
    print(f"Detective Assistant: {response}")
    
    # Interactive chat loop
    while True:
        user_input = input("\nYou: ").strip()
        
        if user_input.lower() in ['quit', 'exit', 'bye']:
            print("Thanks for playing! 👋")
            break
            
        response = await run_agent(
            client, toolbox, agents['mystery-assistant'],
            user_message=user_input, history=chat_history, usage=usage
        )
        
        print(f"Detective Assistant: {response}")
        
        # Check if mystery was solved
        if "Congratulations, you just solved the mystery!" in response:
            print("\n🎉 Mystery solved! Thanks for playing!")
            break
    
    # Print usage statistics
    print("\n")
    print_usage(agents['plot-creator']['model'], usage)

if __name__ == '__main__':
    import sys
    import asyncio
    
    config_file = sys.argv[1]
    
    asyncio.run(main(Path(config_file)))
