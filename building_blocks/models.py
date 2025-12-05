import os
import openai
import together
from openai import OpenAI
from together import Together
from tenacity import retry
from tenacity.retry import retry_if_exception_type
from tenacity.wait import wait_random_exponential


@retry(
	retry=retry_if_exception_type(
			exception_types=(
				openai.RateLimitError,
				openai.APIConnectionError,
				openai.InternalServerError,
				openai.APITimeoutError
			)
		),
		wait=wait_random_exponential(
			multiplier=0.1,
			max=0.5,
		),
	)
def _get_chat_response(client, engine, prompt, sys_prompt, max_tokens, temperature, top_p, n, stop, presence_penalty, frequency_penalty):
	return client.chat.completions.create(
		model=engine,
		messages = [
			{"role": "system", "content": sys_prompt},
			{"role": "user", "content": prompt},
		],
		max_completion_tokens=max_tokens,
		temperature=temperature,
		top_p=top_p,
		n=n,
		presence_penalty=presence_penalty,
		frequency_penalty=frequency_penalty
	)


@retry(
	retry=retry_if_exception_type(
			exception_types=(
				openai.RateLimitError,
				openai.APIConnectionError,
				openai.InternalServerError,
				openai.APITimeoutError
			)
		),
		wait=wait_random_exponential(
			multiplier=0.1,
			max=0.5,
		),
	)
def _get_reasoning_response(client, engine, prompt, temperature, max_completion_tokens, reasoning_effort):
	return client.chat.completions.create(
		model=engine,
		messages = [
			{"role": "user", "content": prompt}
		],
		reasoning_effort=reasoning_effort,
		temperature = temperature,
		max_completion_tokens=max_completion_tokens
	)


def _get_together_response(client, engine, prompt,reasoning_chain, temperature, max_tokens):
	return client.chat.completions.create(
		model=engine,
		messages = [
			{"role": "user", "content": prompt},
			{"role": "assistant", "content": reasoning_chain}
		],
		temperature=temperature,
		max_tokens=max_tokens
	)


class LargeLanguageModel():
	def __init__(self, model_type, model):
		self.model_type = model_type
		self.engine = model

		if self.model_type in ['vllm']:
			openai_api_key = "EMPTY"
			openai_api_base = "http://localhost:8000/v1"
			self.client = OpenAI(
				api_key=openai_api_key,
				base_url=openai_api_base,
			)
		elif self.model_type in ['openai_chat', 'openai_reasoning']:
			self.client = OpenAI(
				api_key=openai.api_key,
			)
		elif self.model_type in ['together']:
			self.client = Together(
				api_key=together.api_key,
			)
		elif self.model_type in ['hyperbolic']:
			self.client = OpenAI(
				api_key=os.getenv("HYPNAME"),
				base_url="https://api.hyperbolic.xyz/v1",
			)

	def predict(self, prompt, sys_prompt, max_tokens, reasoning_chain="", temperature=0.0, reasoning_effort="low", n=1, top_p=1.0, stop = [], presence_penalty=0.0, frequency_penalty=0.0):
		if self.model_type in ["openai_chat", "vllm"]:
			response = _get_chat_response(
				client=self.client,
				engine=self.engine,
				prompt=prompt, 
				sys_prompt=sys_prompt,
				max_tokens=max_tokens,
				temperature=temperature,
				top_p=top_p,
				n=n,
				stop=stop,
				presence_penalty=presence_penalty,
				frequency_penalty=frequency_penalty
			)
			response = response.choices[0].message.content.lstrip('\n').rstrip('\n')
		elif self.model_type in ["openai_reasoning", "hyperbolic"]:
			response = _get_reasoning_response(
       			client=self.client,
				engine=self.engine,
				prompt=prompt,
				temperature=temperature,
				max_completion_tokens=max_tokens,
				reasoning_effort=reasoning_effort
			)
			response = response.choices[0].message.content.lstrip('\n').rstrip('\n')
		elif self.model_type in ["together"]:
			response = _get_together_response(
				client=self.client,
				engine=self.engine,
				prompt=prompt,
    			reasoning_chain=reasoning_chain,
				temperature=temperature,
				max_tokens=max_tokens
			)
			response = response.choices[0].message.content.lstrip('\n').rstrip('\n')
		return response