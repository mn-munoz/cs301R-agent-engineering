import argparse
import json
from pathlib import Path
from time import time

from openai import Client

from usage import print_usage

POKEMON_TYPES = [
    'Bug',
    'Dark',
    'Dragon',
    'Electric',
    'Fairy',
    'Fighting',
    'Fire',
    'Flying',
    'Ghost',
    'Grass',
    'Ground',
    'Ice',
    'Normal',
    'Poison',
    'Psychic',
    'Rock',
    'Steel',
    'Water',
]


def build_schema(row_count: int) -> dict:
    return {
        'type': 'object',
        'additionalProperties': False,
        'properties': {
            'pokemon': {
                'type': 'array',
                'minItems': row_count,
                'maxItems': row_count,
                'items': {
                    'type': 'object',
                    'additionalProperties': False,
                    'properties': {
                        'pokedex_id': {'type': 'integer'},
                        'name': {'type': 'string'},
                        'type1': {'type': 'string', 'enum': POKEMON_TYPES},
                        'type2': {
                            'anyOf': [
                                {'type': 'string', 'enum': POKEMON_TYPES},
                                {'type': 'null'},
                            ]
                        },
                        'total': {'type': 'integer'},
                        'stats': {
                            'type': 'object',
                            'additionalProperties': False,
                            'properties': {
                                'hp': {'type': 'integer'},
                                'attack': {'type': 'integer'},
                                'defense': {'type': 'integer'},
                                'sp_atk': {'type': 'integer'},
                                'sp_def': {'type': 'integer'},
                                'speed': {'type': 'integer'},
                            },
                            'required': [
                                'hp',
                                'attack',
                                'defense',
                                'sp_atk',
                                'sp_def',
                                'speed',
                            ],
                        },
                        'generation': {'type': 'integer'},
                        'legendary': {'type': 'boolean'},
                    },
                    'required': [
                        'pokedex_id',
                        'name',
                        'type1',
                        'type2',
                        'total',
                        'stats',
                        'generation',
                        'legendary',
                    ],
                },
            }
        },
        'required': ['pokemon'],
    }


def build_input(prompt: str, csv_text: str, row_count: int) -> list[dict]:
    return [
        {'role': 'system', 'content': prompt.strip()},
        {
            'role': 'user',
            'content': (
                f'Extract the first {row_count} Pokemon rows from this CSV. '
                'Return JSON that matches the provided schema exactly.\n\n'
                'CSV input:\n'
                f'{csv_text.strip()}'
            ),
        },
    ]


def parse_structured_output(response) -> dict:
    output_text = response.output_text.strip()
    if not output_text:
        raise ValueError('The model returned an empty response.')

    try:
        return json.loads(output_text)
    except json.JSONDecodeError as exc:
        raise ValueError(
            'The model response was not valid JSON. '
            f'Raw response: {output_text}'
        ) from exc


def main(model: str, prompt: str, text: str, row_count: int):
    client = Client()
    start = time()
    response = client.responses.create(
        model=model,
        input=build_input(prompt, text, row_count),
        text={
            'format': {
                'type': 'json_schema',
                'name': 'pokemon_stats_extraction',
                'description': 'Structured extraction of Pokemon CSV rows.',
                'strict': True,
                'schema': build_schema(row_count),
            }
        },
    )
    structured_output = parse_structured_output(response)
    print(json.dumps(structured_output, indent=2))

    print(f'{round(time()-start, 2)} seconds elapsed')
    # print_usage(model, response.usage)


if __name__ == "__main__":
    parser = argparse.ArgumentParser('AI Response')
    parser.add_argument('prompt_file', type=Path)
    parser.add_argument('input_file', type=Path)
    parser.add_argument('--model', default='gpt-5-nano')
    parser.add_argument('--rows', type=int, default=3)
    args = parser.parse_args()

    current_dir = Path(__file__).resolve().parent
    args.prompt_file = current_dir / args.prompt_file
    args.input_file = current_dir / args.input_file

    main(
        args.model,
        args.prompt_file.read_text(),
        args.input_file.read_text(),
        args.rows,
    )
