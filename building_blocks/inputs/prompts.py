# from examples import *

def get_prompt(prompt_type, dataset, anno_type="all", params=None):
	sys_prompt = ""
	prompt = ""
 
	if prompt_type == "annotate":
		sys_prompt = "You are a helpful assistant for annotating a provided reasoning chain. You must not alter the provided chain in any way, except to put in-place annotation tags. Just output the complete annotated reasoning chain only and nothing else."
  
		if anno_type == "all":
			
			if dataset == 'aime':
				from inputs.examples import aime_examples as ex
    
			elif dataset == 'math500':
				from inputs.examples import math_examples as ex
			
			elif dataset == 'safety':
				from inputs.examples import safety_examples as ex
			
			elif dataset == 'hallucination':
				from inputs.examples import hallucination_examples as ex

			elif dataset == 'psycho':
				from inputs.examples import psycho_examples as ex

			prompt = f"""Given a chain of reasoning from a different reasoning model such as R1, we have identified several steps we would like you to tag. The steps are as follows:

1. Problem definition (denoted by <DEFINE> tags). This cycle redefines the problem to answer and often ends by indicating what it needs to deliver as the final answer, e.g., ``I need to find ...''. This step does not contain any reasoning towards a solution. There is only one Definition step.

2. The Blooming Step (denoted by <BLOOM> tags) First cycle of reasoning. This includes an initial exploration of the problem and defines some premises, by breaking the problem into subproblems. It must give an answer to the given question and may or may not qualify its confidence with something like "That sounds right" or "That doesn't make sense" (this is denoted by <v> tags). There is only one Bloom step.

3. Reconsideration Step(s) (denoted by <CYCLE> tags). These stages reconsider some of the initial assumptions, double-check a potential error, or introduce a new approach to solve the problem (these reconsiderations are denoted by <r> tags). Through this cycle of reasoning, an answer may be reached. It may or may not end with some confidence qualification in the answer (denoted with <v> tags). There may be several reasoning cycles. 

4. Final decision (denoted by <FINAL> tags) A final answer is reached. This may be indicated by a phrase like ``I'm confident...'' and denotes the final answer. There is only one Final step.

The stage may change within a single paragraph. Note that all text in the reasoning chain must be annotated to be a part of any of the 4 stages. We have annotated an example for you here:\n\n{ex[0]}

Now, please annotate this chain of reasoning following the previous example. Only add the tags. Do not otherwise modify the provided text:\nGiven the following question:\n{params[0]}\n\nThe chain of reasoning is:\n\n{params[1]}"""
		
	return sys_prompt, prompt