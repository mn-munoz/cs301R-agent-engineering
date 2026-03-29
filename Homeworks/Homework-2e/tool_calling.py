import argparse
import asyncio
from pathlib import Path
import json

import gradio as gr
from openai import AsyncOpenAI

from tools import ToolBox
from usage import print_usage, format_usage_markdown
from codebot import execute_code

our_tools = ToolBox()

our_tools.tool(execute_code)

class ChatAgent:
    def __init__(self, model: str, prompt: str, show_reasoning: bool, reasoning_effort: str | None):
        self._ai = AsyncOpenAI()
        self.model = model
        self.show_reasoning = show_reasoning
        self.reasoning = {}
        if show_reasoning:
            self.reasoning['summary'] = 'auto'
        if 'gpt-5' in self.model and reasoning_effort:
            self.reasoning['effort'] = reasoning_effort

        self.usage = []
        self.usage_markdown = format_usage_markdown(self.model, [])

        self._history = []
        self._prompt = prompt
        if prompt:
            self._history.append({'role': 'system', 'content': prompt})

    async def get_response(self, user_message: str):
        self._history.append({'role': 'user', 'content': user_message})

        while True:
            tools = our_tools.tools + [{'type': 'web_search'}]
            response = await self._ai.responses.create(
                input=self._history,
                model=self.model,
                reasoning=self.reasoning,
                tools=tools
            )

            self.usage.append(response.usage)
            self.usage_markdown = format_usage_markdown(self.model, self.usage)
            self._history.extend(
                response.output
            )

            for item in response.output:
                if item.type == 'reasoning':
                    for chunk in item.summary:
                        yield 'reasoning', chunk.text

                elif item.type == 'function_call':
                    yield 'reasoning', f'{item.name}({item.arguments})'

                    func = our_tools.get_tool_function(item.name)
                    args = json.loads(item.arguments)
                    result = func(**args)
                    self._history.append({
                        'type': 'function_call_output',
                        'call_id': item.call_id,
                        'output': str(result)
                    })
                    yield 'reasoning', str(result)

                elif item.type == 'message':
                    for chunk in item.content:
                        yield 'output', chunk.text
                    return

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        print_usage(self.model, self.usage)


async def _main_console(agent_args):
    with ChatAgent(**agent_args) as agent:
        while True:
            message = input('User: ')
            if not message:
                break
            
            reasoning_complete = True
            if agent.show_reasoning:
                print('Reasoning '.center(30, '-'))
                reasoning_complete = False
            
            last_type = ''
            async for text_type, text in agent.get_response(message):
                if text_type == 'output':
                    print()
                    print('-' * 30)
                    print()
                    print('Agent: ')
                    reasoning_complete = True
                    
                if last_type != text_type:
                    print(f'\n{text_type}: ', end='', flush=True)       # emit a newline between types
                    last_type = text_type

                print(text, end='', flush=True)
            print()
            print()
        


def _main_gradio(agent):
    # Constrain width with CSS and center
    css = """
    /* limit overall Gradio app width and center it */
    .gradio-container, .gradio-app, .gradio-root {
      width: 120ch;
      max-width: 120ch !important;
      margin-left: auto !important;
      margin-right: auto !important;
      box-sizing: border-box !important;
    }
    """

    usage_view = gr.Markdown(format_usage_markdown(agent.model, []))

    with gr.Blocks(css=css, theme=gr.themes.Monochrome()) as demo: #type: ignore
        async def get_response(message, chat_view_history):
            response = await agent.get_response(message)
            usage_content = format_usage_markdown(agent.model, agent.usage)
            return response, usage_content

        with gr.Row():
            with gr.Column(scale=5):
                bot = gr.Chatbot(
                    label=' ',
                    height=600,
                    resizable=True,
                )
                chat = gr.ChatInterface(
                    chatbot=bot,
                    fn=get_response,
                    additional_outputs=[usage_view]
                )

            with gr.Column(scale=1):
                usage_view.render()

    demo.launch()


def main(prompt_path: Path, model: str, show_reasoning, reasoning_effort: str | None, use_web: bool):
    agent_args = dict(
        model=model,
        prompt=prompt_path.read_text() if prompt_path else '',
        show_reasoning=show_reasoning,
        reasoning_effort=reasoning_effort

    )

    if use_web:
        _main_gradio(agent_args)
    else:
        asyncio.run(_main_console(agent_args))


# Launch app
if __name__ == "__main__":
    parser = argparse.ArgumentParser('ChatBot')
    parser.add_argument('prompt_file', nargs='?', type=Path, default=None)
    parser.add_argument('--web', action='store_true')
    parser.add_argument('--model', default='gpt-5-nano')
    parser.add_argument('--show-reasoning', action='store_true')
    parser.add_argument('--reasoning-effort', default='medium', choices=['none', 'low', 'medium', 'high'])
    args = parser.parse_args()
    main(args.prompt_file, args.model, args.show_reasoning, args.reasoning_effort, args.web)
