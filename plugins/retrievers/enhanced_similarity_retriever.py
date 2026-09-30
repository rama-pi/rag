import spacy
import nltk
nltk.download('wordnet')
from nltk.corpus import wordnet
from collections import Counter
import numpy as np

from framework.base_classes import Retriever
from framework.helpers import cosine_similarity

'''
 return N ranked chunks using vocabulary-frequency vectors and cosine similarity.
'''
class EnhancedSimilarityRetriever(Retriever, retriever_name="enhanced_similarity_retriever"):
    def __init__(self, retriever_name):
        self.name = retriever_name
        self.nlp = spacy.load("en_core_web_sm")
        return
    @staticmethod
    def get_synonyms(self, word):
        synonyms = set()
        for syn in wordnet.synsets(word):
            for lemma in syn.lemmas():
                synonyms.add(lemma.name())
        return synonyms
    @staticmethod
    def expand_with_synonyms(self, words):
        expanded_words = words.copy()
        for word in words:
            expanded_words.extend(self.get_synonyms(self, word))
        return expanded_words
    @staticmethod
    def preprocess_text(self,text):
        # filter out punctuations, stop words, reduce each words to its lemma
        doc = self.nlp(text.lower())
        lemmatized_words = []
        for token in doc:
            if token.is_stop or token.is_punct:
                continue
            lemmatized_words.append(token.lemma_)
        return lemmatized_words
    @staticmethod
    def calculate_enhanced_similarity(self, text1, text2):
        # Preprocess and tokenize texts and reduce to lemma's
        words1 = self.preprocess_text(text1)
        words2 = self.preprocess_text(text2)

        # Expand with synonyms
        words1_expanded = self.expand_with_synonyms(words1)
        words2_expanded = self.expand_with_synonyms(words2)

        # Count word frequencies
        freq1 = Counter(words1_expanded)
        freq2 = Counter(words2_expanded)

        # Create a set of all unique words
        unique_words = set(freq1.keys()).union(set(freq2.keys()))

        # Create frequency vectors
        vector1 = [freq1[word] for word in unique_words]
        vector2 = [freq2[word] for word in unique_words]

        # Calculate cosine similarity
        return cosine_similarity(vector1, vector2)
        '''
        calculate cosine similarity between given 2 chunks.
        normally one is stored chunk of doc, other is query chunk
        '''
    def retrieve(self, chunk: str, chunks: list, top_n: int):
        d = {}
        # get cosine pair
        for (chunk_id, doc_id, chunk) in chunks:
            cos_sim =  self.calculate_enhanced_similarity(chunk, c)
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


