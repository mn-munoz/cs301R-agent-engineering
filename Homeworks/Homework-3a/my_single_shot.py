import json
from typing import TypedDict

from pathlib import Path
import yaml
from openai import AsyncOpenAI
from usage import print_usage
from tools import ToolBox

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
            
async def main(agent_config: Path, message: str):
    client = AsyncOpenAI()
    
    agent = yaml.safe_load(agent_config.read_text())
    
    history = []
    usage = []
    
    response = await run_agent(
        client, toolbox, agent,
        message, history, usage
    )
    print('Final response:', response)
    print()
    print_usage(agent['model'], usage)
    
if __name__ == '__main__':
    import sys
    import asyncio
    
    asyncio.run(main(Path(sys.argv[1]), sys.argv[2]))