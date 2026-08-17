from abc import ABC, abstractmethod

import ollama

from framework.base_classes import Model

class OllamaModel(Model, model_name="llama3.2", model_modes=['stream', 'nostream']):
# model adapter 
# prompt_eval_count - The number of input tokens the model processed before it started generating an answer
# eval_count - The number of output tokens the model generated.
    #stateless
    def __init__(self, model_name, model_mode):
        self.model_name = model_name
        self.model_mode = model_mode
    def ask(self, messages):
        answer = ''
        if self.model_mode == 'stream':
            try:
                stream = ollama.chat(
                        model = self.model_name,
                        messages = messages,
                        stream = True
                        )
                for chunk in stream:
                    print(chunk['message']['content'], end='', flush=True)
                    answer += chunk['message']['content']
                print()
                return answer
            except Exception as e:
                print(f"Error connecting to Ollama: {e}")
                print("Double check that the Ollama app or server is running in the background!")
        else:
            # not currently validating if other is nostream mode
            answer = ollama.chat(
                    model=self.model_name,
                    messages=messages
                    )
            print(answer['message']['content'])
            print(f"Token counts: input = {answer['prompt_eval_count']} output = {answer['eval_count']}")
            print(f"Eval time: input = {answer['prompt_eval_duration']} output = {answer['eval_duration']}")
            return answer['message']['content']
