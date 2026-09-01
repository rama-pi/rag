from abc import ABC, abstractmethod
from collections import Counter
import math

from framework.base_classes import Embedder

class BM25_embedder(Embedder, embed_model="BM25"):
    def __init__(self, embed_model):
        # setup hyper-parameters
        k1 = 1.5
        b = 0.75
        pass
    def embed(self, chunks: list):
        for chunks in chunks:
            # build chunk vocab
            vocab = set(word for log in chunk for word in chunk.split(','))
            vocab_to_idx = {word: idx for idx, word in enumerate(vovab)}

            # calculate IDF





