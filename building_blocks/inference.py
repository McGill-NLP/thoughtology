import os
import argparse
import datetime
import random
import openai
import together
from models import LargeLanguageModel
from inputs.prompts import get_prompt
from datasets import load_dataset
import time
import json
import tqdm
import pdb

import concurrent.futures
from concurrent.futures import ThreadPoolExecutor, as_completed

def build_parser():
	parser = argparse.ArgumentParser(description='Generate')

	parser.add_argument('-run_name', type=str, default='default', help='run name for logs')
	parser.add_argument('-out_dir', type=str, default='outputs/', help='Output Directory')
	parser.add_argument('-in_dir', type=str, default='inputs/predictions/', help='Input Directory')
	parser.add_argument('-stop', type=list, default=[], help='When to stop generation')
	parser.add_argument('-prompt_type', type=str, default='annotate', choices=['annotate'], help='prompt type')
	parser.add_argument('-model_type', type=str, default='openai_chat', choices=['hyperbolic', 'together', 'openai_reasoning', 'openai_chat', 'vllm'], help='Which type of model to use')
	parser.add_argument('-model', type=str, default='gpt-4.1-nano', help='Which model to use')
	parser.add_argument('-predictions_file', type=str, default='aime_qwen3.json', help='Which predictions file to use')
	parser.add_argument('-max_tokens', type=int, default=32000, help='Maximum number of tokens')
	parser.add_argument('-temperature', type=float, default=0.6, help='Sampling temperature')
	parser.add_argument('-reasoning_effort', type=str, default='low', choices=['low', 'medium', 'high'], help='Reasoning effort')
	parser.add_argument('-top_p', type=float, default=1.0, help='top what percentage of tokens to be considered') 
	parser.add_argument('-n', type=int, default=0, help='Number of questions to be investigated') 
	parser.add_argument('-start_num', type=int, default=0, help="What index number to start inference from")
	parser.add_argument('-anno_type', type=str, default='all', choices=['all_t', 'all_c', 'all', 'ans', 'cycle', 'tag'], help='What to annotate. In the final paper, we use "all" or "ans" for answer-only annotations') 
	parser.add_argument('-debug', type=bool, default=False, help="If debugging")
	parser.add_argument(
        '-num_workers',
        type=int,
        default=8,
        help='Number of parallel workers for API calls'
    )

	return parser


def process_one_example(i, d, args, model):
    # Choose question field based on dataset
    if args.dataset in ['aime', 'math500']:
        question = d['Problem']
    elif args.dataset in ['safety', 'hallucination', 'psycho']:
        question = d['prompt']
    else:
        question = d['question']

    params = [question]

    # Add answer for annotate-type prompts
    if args.prompt_type == "annotate":
        ans = d['Answer']
        if "<think>" not in ans:
            ans = "<think>\n" + ans
        if "</think>" in ans:
            ans = ans.split("</think>")[0] + "</think>"
        params.append(ans)

    sys_prompt, prompt = get_prompt(args.prompt_type, args.dataset, args.anno_type, params)

    t0 = time.time()
    res = model.predict(
        prompt=prompt,
        sys_prompt=sys_prompt,
        max_tokens=args.max_tokens,
        temperature=args.temperature,
        reasoning_effort=args.reasoning_effort,
        top_p=args.top_p,
        stop=args.stop,
    )
    t1 = time.time()

    return {
        'id': i,
        'question': question,
        'answer': res,
        'time': t1 - t0,
    }


def main(args):
    # Single model instance shared across threads
    model = LargeLanguageModel(model_type=args.model_type, model=args.model)

    with open(os.path.join(args.in_dir, args.predictions_file)) as f:
        raw = json.load(f)
        data = raw[:args.n] if args.n else raw

    print(f"Loaded {len(data)} samples from {args.predictions_file} for {args.anno_type} {args.prompt_type} task")

    if args.debug:
        # keep simple sequential behavior for debug
        res = process_one_example(0, data[0], args, model)
        print(res)
        return

    # Pre-allocate list so we can keep original order
    responses = [None] * len(data)

    with ThreadPoolExecutor(max_workers=args.num_workers) as executor:
        future_to_idx = {
            executor.submit(process_one_example, i, d, args, model): i
            for i, d in enumerate(data)
        }

        for future in tqdm.tqdm(as_completed(future_to_idx), total=len(future_to_idx)):
            result = future.result()
            responses[result['id']] = result

    # Filter out any Nones (shouldn't happen unless there was an error you handle)
    responses = [r for r in responses if r is not None]

    # Single JSON write at the end
    out_path = os.path.join(args.out_dir, args.out_file_name)
    with open(out_path, "w") as f:
        json.dump(responses, f, indent=4)

    print(f"Saved {len(responses)} responses to {out_path}")



if __name__ == "__main__":
    parser = build_parser()
    args = parser.parse_args()

    args.out_dir_name = args.out_dir

    cur_time = str(datetime.datetime.now())
    disp_time = cur_time.split()[0] + "-" + cur_time.split()[1].split(".")[0]

    if args.run_name == "default":
        args.run_name = args.predictions_file.split('.json')[0] + "_" + args.prompt_type

    args.run_name = args.run_name.replace("/", "-")

    args.out_dir = os.path.join(args.out_dir, args.run_name)
    args.dataset = args.predictions_file.split('_')[0]
    args.out_file_name = f"{args.anno_type}_{args.predictions_file}"

    if not os.path.exists(args.out_dir):
        os.makedirs(args.out_dir)

    openai.api_key = os.getenv("OPENAI_API_KEY")
    together.api_key = os.getenv("TOGETHER_API_KEY")

    main(args)