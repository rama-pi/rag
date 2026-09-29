

from framework.base_classes import Retriever
from framework.helpers import cosine_similarity

class DenseSimilarityRetriever(Retriever, retriever_name="dense_similarity_retriever"):
    def __init__(self):
        return
    def retrieve(self, vector: list, vectors: list, chunks: list, top_n: int):
        d = {}
        for vec, (chunk_id, doc_id, chunk) in zip(vectors, chunks):
            cos_sim = cosine_similarity(vector, vec)
            d[chunk_id] = {
                    "doc_id": doc_id,
                    "chunk": chunk,
                    "score": cos_sim
                    }
        top_n = sorted(
                d.items(), key=lambda item: item[1]['score'], reverse=True
        )[:top_n]

        return top_n


