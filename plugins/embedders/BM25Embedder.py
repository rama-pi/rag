from abc import ABC, abstractmethod
from collections import Counter
import math

from framework.base_classes import Embedder

# sparse embedder, based on vocab
class BM25_embedder(Embedder, embed_model="BM25"):
    def __init__(self, embed_model):
        # setup hyper-parameters
        self.k1 = 1.5
        self.b = 0.75
        # BM25 smoothing constant 
        self.s = 0.5
        pass
    def embed(self, chunks: list):
        # build chunk vocab
        vocab = set(word for chunk in chunks for word in chunk.split())
        vocab_to_idx = {word: idx for idx, word in enumerate(vocab)}

        # treat chunks as corpus / doc's
        # avg len of corpus / all docs in words / vocab / tokens
        # this avg len takes all **related** docs into consideration
        N = len(chunks)
        avg_chunk_len = sum(len(chunk.split()) for chunk in chunks) / N
        # calculate DF, IDF
        df = Counter(word for chunk in chunks for word in set(chunk.split()))
        idf = {word: math.log((N -df[word] + self.s)/ (df[word] + self.s) +1) for word in vocab}


        # compute sparse embedding per chunk / doc
        sparse_list = []
        for chunk in chunks:
            tf = Counter(chunk.split())
            log_len = len(chunk.split())
            embedding = {}

            for word, freq in tf.items():
                if word in vocab:
                    idx = vocab_to_idx[word]
                    score = idf[word] * (freq * (self.k1 + 1)) / (freq + self.k1 * (1 - self.b + self.b * log_len / avg_chunk_len))
                    embedding[idx] = score
            sparse_list.append(embedding)
        return sparse_list
