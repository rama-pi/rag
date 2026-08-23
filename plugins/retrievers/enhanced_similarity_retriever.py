import spacy
import nltk
nltk.download('wordnet')
from nltk.corpus import wordnet
from collections import Counter
import numpy as np

from framework.base_classes import Retriever

class EnhancedSimilarityRetriever(Retriever, retriever_name="enhanced_similarity_retriever"):
    def __init__(self, retriever_name):
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
        words1 = self.preprocess_text(self, text1)
        words2 = self.preprocess_text(self, text2)

        # Expand with synonyms
        words1_expanded = self.expand_with_synonyms(self, words1)
        words2_expanded = self.expand_with_synonyms(self, words2)

        # Count word frequencies
        freq1 = Counter(words1_expanded)
        freq2 = Counter(words2_expanded)

        # Create a set of all unique words
        unique_words = set(freq1.keys()).union(set(freq2.keys()))

        # Create frequency vectors
        vector1 = [freq1[word] for word in unique_words]
        vector2 = [freq2[word] for word in unique_words]

        # Calculate cosine similarity
        cosine_similarity = np.dot(vector1, vector2) / (np.linalg.norm(vector1) * np.linalg.norm(vector2))
        return cosine_similarity
    def retrieve(self, text1, text2):
        if not isinstance(text1, str):
            text1 = " ".join(text1)
        if not isinstance(text2, str):
            text2 = " ".join(text2)

        cs =  self.calculate_enhanced_similarity(self,text1, text2)
        if cs:
            return {"matched": True,
                    "score": cs
                    }
        else:
            return None


