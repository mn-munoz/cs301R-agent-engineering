import argparse
import asyncio
import sys
from pathlib import Path

import gradio as gr
from openai import AsyncOpenAI

from usage import print_usage, format_usage_markdown

REASONING_EFFORT_CHOICES = ('none', 'minimal', 'low', 'medium', 'high', 'xhigh')


def _build_reasoning_config(model: str, reasoning_effort: str | None):
    if reasoning_effort is None:
        if model.startswith('gpt-5'):
            return {'effort': 'low'}
        return None

    if model == 'gpt-5-pro' and reasoning_effort != 'high':
        raise ValueError('Model "gpt-5-pro" only supports reasoning effort "high".')

    if model.startswith('gpt-5.1') and reasoning_effort in {'minimal', 'xhigh'}:
        raise ValueError(
            f'Model "{model}" does not support reasoning effort "{reasoning_effort}".'
        )

    if model.startswith('gpt-5') and not model.startswith('gpt-5.1') and reasoning_effort == 'none':
        raise ValueError(
            f'Model "{model}" does not support reasoning effort "none".'
        )

    return {'effort': reasoning_effort}


class ChatAgent:
    def __init__(self, model: str, prompt, reasoning_effort: str | None = None) -> None:
        self._ai = AsyncOpenAI()
        self.usage = []
        self.model = model
        self.reasoning = _build_reasoning_config(model, reasoning_effort)
        self._prompt = prompt
        self._history = []
        if prompt:
            self._history.append({'role': 'system', 'content': prompt})
            
    async def get_response(self, user_message: str) -> str:
        self._history.append({'role': 'user', 'content': user_message})

        response = await self._ai.responses.create(
            input=self._history,
            model=self.model,
            reasoning=self.reasoning
        )
        self.usage.append(response.usage)
        self._history.extend(
            response.output
        )
        return response.output_text
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        print_usage(self.model, self.usage)


def _chat_container(agent):
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
    
    with gr.Blocks(css=css) as demo:
        async def get_response(message, chat_view_history):
            response = await agent.get_response(message)
            usage_content = format_usage_markdown(agent.model, agent.usage)
            return response, usage_content
        
        with gr.Row():
            with gr.Column(scale = 4):
                bot = gr.Chatbot(
                    label = ' ',
                    height = 500,
                    resizable = True,
                )
                chat = gr.ChatInterface(
                    chatbot = bot,
                    fn=get_response,
                    additional_outputs=[usage_view]
                )
                
                with gr.Column(scale = 1):
                    usage_view.render()
                    
    demo.launch()
                
            
def main(prompt_path: Path, model: str, reasoning_effort: str | None):
    with ChatAgent(model, prompt_path.read_text(), reasoning_effort) as agent:
        _chat_container(agent)

if __name__ == "__main__":
    parser = argparse.ArgumentParser('ChatBot')
    parser.add_argument('prompt_file', type=Path)
    parser.add_argument('--model', default='gpt-5-nano')
    parser.add_argument('--reasoning-effort',choices=REASONING_EFFORT_CHOICES)
    args = parser.parse_args()
    
    current_dir = Path(__file__).resolve().parent
    args.prompt_file = current_dir / args.prompt_file

    main(args.prompt_file, args.model, args.reasoning_effort)
