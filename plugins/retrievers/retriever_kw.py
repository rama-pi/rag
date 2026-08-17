from abc import ABC, abstractmethod

'''
from retriever import Retriever
'''

from framework.base_classes import Retriever

# repeat of target kw in candidate is ignored
# as set and set intersection is used here to
# get score.
class Retriever_KW(Retriever, retriever_name='kw'):
    def __init__(self, retriever_name):
        pass
    def retrieve(self, past_q_w, curr_q_w):
        rs = past_q_w.intersection(curr_q_w)
        if len(rs):
            return {"matched": True,
                    "score": len(rs)
                    }
        else:
            return None
