import argparse
import asyncio
import sys
from pathlib import Path

import gradio as gr
from openai import AsyncOpenAI

from usage import print_usage, format_usage_markdown

class ChatAgent:
    def __init__(self, model: str, prompt) -> None:
        self._ai = AsyncOpenAI()
        self.usage = []
        self.model = model
        self.reasoning = None
        if 'gpt-5' in self.model:
            self.reasoning = {'effort': 'low'}
        self._prompt = prompt
        self._history = []
        if prompt:
            self._history.append({'role': 'system', 'content': prompt})
            
    async def get_response(self, user_message: str) -> str:
        self._history.append({'role': 'user', 'content': user_message})

        response = await self._ai.responses.create(
            input=self._history,
            model=self.model,
            reasoning= self.reasoning
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
                
            
def main(prompt_path: Path, model: str):
    with ChatAgent(model, prompt_path.read_text()) as agent:
        _chat_container(agent)

if __name__ == "__main__":
    parser = argparse.ArgumentParser('ChatBot')
    parser.add_argument('prompt_file', type=Path)
    parser.add_argument('--model', default='gpt-5-nano')
    args = parser.parse_args()
    
    current_dir = Path(__file__).resolve().parent
    args.prompt_file = current_dir / args.prompt_file

    main(args.prompt_file, args.model)