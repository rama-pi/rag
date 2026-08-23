import re
from abc import ABC, abstractmethod

from framework.base_classes import Retriever
from framework.helpers import remove_unwanted

class Retriever_RE(Retriever, retriever_name='re'):
    def __init__(self, retriever_name):
        pass
    #def retrieve(self, past_q_w, curr_q_w):
    def retrieve(self, past_q_a: str, curr_q: str):
        # to increase the search hit search past Q & A too
        past_q_w, curr_q_w = remove_unwanted(past_q_a, curr_q)
        pattern = "|".join(rf"\b{w}\b" for w in curr_q_w)
        past_q = " ".join(past_q_w)
        l = len(re.findall(pattern, past_q))
        if l:
            return {"matched": True,
                    "score": l
                    }
        else:
            return None
