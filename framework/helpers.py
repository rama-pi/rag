import os, sys, json, re, string, importlib
from pathlib import Path
import numpy as np

import spacy
import nltk
nltk.download('wordnet')
from nltk.corpus import wordnet
from collections import Counter
import numpy as np


class ExistsCheck:
    def __eq__(self, other):
        # SQL returned None means the document already exists!
        return other is None

    def __radd__(self, other):  # Built-in right side operator fallback helper
        return self.__eq__(other)

# Define your keyword
EXISTS = ExistsCheck()

'''
 remove these words from chunks and query.
 these don;t contribute any to similarity computation.
 benefits:
   - either frquency or nomic embedding will be quicker
   - storage space
'''
ignore_words = {
        "the",
        "a",
        "an",
        "is",
        "are",
        "of",
        "to",
        "for",
        "in",
        "on",
        "at",
        "what",
        "how",
        "why",
        "explain",
        "give"
        }

'''
def remove_unwanted(past_q, curr_q):
    # normalize whitespaces
    past_q = " ".join(past_q.split())
    curr_q = " ".join(curr_q.split())
    # lowercase, remove punctuation
    past_q_w = {w.strip(string.punctuation) for w in past_q.lower().split()}
    curr_q_w = {w.strip(string.punctuation) for w in curr_q.lower().split()}
    # remove stop words
    #past_q_w = {w for w in past_q_w if w not in ignore_words}
    #curr_q_w = {w for w in curr_q_w if w not in ignore_words}
    past_q = " ".join([w for w in past_q_w if w not in ignore_words])
    curr_q = " ".join([w for w in curr_q_w if w not in ignore_words])
    # return lists of words
    return (past_q, curr_q)
'''
def remove_unwanted(chunk: str):
    # normalize whitespaces
    chunk = " ".join(chunk.split())
    # lowercase, remove punctuation
    chunk = [w.strip(string.punctuation) for w in chunk.lower().split()]
    # remove stop words
    chunk = " ".join([w for w in chunk if w not in ignore_words])
    # return preprocessed chunk
    return chunk

def cosine_similarity(vector1, vector2):
    return np.dot(vector1, vector2) / (
        np.linalg.norm(vector1) * np.linalg.norm(vector2)
    )
def get_synonyms(word):
    synonyms = set()
    for syn in wordnet.synsets(word):
        for lemma in syn.lemmas():
            synonyms.add(lemma.name())
    return synonyms
def expand_with_synonyms(words):
    expanded_words = words.copy()
    for word in words:
        expanded_words.extend(get_synonyms(word))
    return expanded_words
def preprocess_text(text):
    # filter out punctuations, stop words, reduce each words to its lemma
    nlp = spacy.load("en_core_web_sm")
    doc = nlp(text.lower())
    lemmatized_words = []
    for token in doc:
        if token.is_stop or token.is_punct:
            continue
        lemmatized_words.append(token.lemma_)
    return lemmatized_words
def calculate_enhanced_similarity(text1, text2):
    # Preprocess and tokenize texts and reduce to lemma's
    words1 = preprocess_text(text1)
    words2 = preprocess_text(text2)

    # Expand with synonyms
    words1_expanded = expand_with_synonyms(words1)
    words2_expanded = expand_with_synonyms(words2)

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

"""
    Dynamically loads all Python modules in a given plugins subfolder.
    Example: discover("plugins/models")
"""
def discover(plugin_subfolder: str):
    # 1. Convert the folder path to a proper path object relative to project root
    base_path = Path(plugin_subfolder)
    if not base_path.exists():
        print(f"[Framework Warning] Plugin directory {plugin_subfolder} not found.")
        return

    # 2. Convert the folder path structure to a Python module path notation
    # e.g., "plugins/models" becomes "plugins.models"
    package_prefix = plugin_subfolder.replace("/", ".").strip(".")

    # 3. Iterate over every entry in the directory
    for entry in os.listdir(base_path):
        # Skip hidden files (like .DS_Store), private files (__init__.py), and directories
        if entry.startswith('.') or entry.startswith('__') or not entry.endswith('.py'):
            continue

        # Strip the '.py' extension to get the module name
        module_file_name = entry[:-3]

        # Construct the absolute import module path string (e.g., "plugins.models.llama_model")
        full_module_name = f"{package_prefix}.{module_file_name}"

        try:
            print(f"[Framework] Dynamically loading plugin: {full_module_name}")
            importlib.import_module(full_module_name)
        except Exception as e:
            print(f"[Framework Error] Failed to load plugin {full_module_name}: {e}")



