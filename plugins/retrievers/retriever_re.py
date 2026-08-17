import re
from abc import ABC, abstractmethod

from framework.base_classes import Retriever

class Retriever_RE(Retriever, retriever_name='re'):
    def __init__(self, retriever_name):
        pass
    def retrieve(self, past_q_w, curr_q_w):
        # to increase the search hit search Q & A too
        pattern = "|".join(rf"\b{w}\b" for w in curr_q_w)
        past_q = " ".join(past_q_w)
        l = len(re.findall(pattern, past_q))
        if l:
            return {"matched": True,
                    "score": l
                    }
        else:
            return None
