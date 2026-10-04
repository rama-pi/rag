from framework.base_classes import Retriever
from framework.helpers import cosine_similarity, calculate_enhanced_similarity

class EnhancedSimilarityRetriever(Retriever, retriever_name="enhanced_similarity_retriever"):
    def __init__(self, retriever_name):
        self.name = retriever_name
        return
        '''
            calculate cosine similarity between given 2 chunks.
            normally one is stored chunk of docs, other is query chunk.
            return N ranked chunks using vocabulary-frequency vectors and cosine similarity.
        '''
    def retrieve(self, qchunk: str, chunks: list, top_n: int):
        d = {}
        # get cosine pair
        for (chunk_id, doc_id, chunk) in chunks:
            cos_sim =  calculate_enhanced_similarity(qchunk, chunk)
            d[chunk_id] = {
                    "doc_id": doc_id,
                    "chunk": chunk,
                    "score": cos_sim
                    }
        top_n = sorted(
                d.items(), key=lambda item: item[1]['score'], reverse=True
        )[:top_n]

        return top_n

        '''
        if cs:
            return {"matched": True,
                    "score": cosSim
                    }
        else:
            return None
        '''


