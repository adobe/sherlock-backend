import json
import sys
import argparse

sys.path.append('')
from qa_pipeline.pipeline import QAPipeline


def _answer_multi_choice(item, pipeline):
    choices = [f'Варіант {index + 1}: {choice["text"]}'
               for index, choice in zip(range(len(item['answers'])), item['answers'])]
    query = item['question'] + ': ' + '; '.join(choices)
    answer = pipeline.run(query, False, prompt_template='prompts/simple_prompt_multi_choice.txt').strip()
    if 'Варіант' in answer:
        answer = answer[answer.index('Варіант') + 8]
        if ':' in answer:
            answer = answer[0:answer.index(':')]
        try:
            index = int(answer)
        except:
            index = 1  # default to something
    else:
        index = 1
    markers = [choice['marker'] for choice in item['answers']]
    if index > 0 and index <= len(markers):
        return markers[index - 1]
    else:
        return markers[0]


def _answer_freeform(item, pipeline):
    query = item['instruction']
    return pipeline.run(query, False, prompt_template='prompts/simple_prompt_freeform.txt').strip()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog="Sherlock QA",
                                     description="Entry point for the Sherlock Baby LLM",
                                     epilog="Github: https://github.com/adobe/sherlock-backend")
    parser.add_argument("--input-file", required=True)
    parser.add_argument("--output-file", required=True)
    args = parser.parse_args()
    f_out = open(args.output_file, 'w')
    input_lines=open(args.input_file, 'r').readlines()
    input_lines=input_lines[0:]
    pipeline = QAPipeline()
    for line in input_lines:
        item = json.loads(line)
        if 'answers' in item:
            result = _answer_multi_choice(item, pipeline)
        else:
            result = _answer_freeform(item, pipeline)
        print("\n\nASD FGF\n\n")

        f_out.write(json.dumps({'answer': result}) + '\n')
        f_out.flush()
    f_out.close()
