from abc import ABC, abstractmethod

'''
from retriever import Retriever
'''

from framework.base_classes import Retriever
from framework.helpers import remove_unwanted

# repeat of target kw in candidate is ignored
# as set and set intersection is used here to
# get score.
class Retriever_KW(Retriever, retriever_name='kw'):
    def __init__(self, retriever_name):
        pass
    def retrieve(self, past_q_a: str, curr_q: str):
        # to increase the search hit search past Q & A too
        past_q_w, curr_q_w = remove_unwanted(past_q_a, curr_q)
        rs = past_q_w.intersection(curr_q_w)
        if len(rs):
            return {"matched": True,
                    "score": len(rs)
                    }
        else:
            return None
