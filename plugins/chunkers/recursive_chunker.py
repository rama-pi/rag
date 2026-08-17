import os, sys, json, re, string
from datetime import datetime
from abc import ABC, abstractmethod

from framework.base_classes import Chunker

'''
separators used by LangChain’s RecursiveCharacterTextSplitter have a strict order of precedence.

The splitter looks at the list of separators from left to right, moving from the largest logical blocks 
(like paragraphs) to the smallest individual characters.

The Default Precedence Order :-

LangChain uses the following list of separators, ordered from highest precedence to lowest:
    1. "\n\n" (Double newlines / Paragraphs)"
    2. "\n" (Single newline / Lines)
    3. " " (Spaces / Words)
    4. "" (Empty string / Individual characters)

How the Precedence Works
    - Top-down splitting: The chunker first tries to split the text using the first separator (\n\n).
    - Fallback mechanism: If a resulting chunk is still larger than your target chunk_size, 
        it moves to the next separator (\n) to split that specific oversized chunk.
    - Granular reduction: It repeats this process down the list (" " and then "") until every single 
        chunk fits within your defined chunk_size.
    - Context preservation: By processing the separators in this specific order, the chunker keeps 
        paragraphs and sentences together as much as possible, preventing semantic meaning from being lost.
'''

"""
RecursiveChunker V1

Features:
- Recursive separators
- Word-preserving chunks
- Configurable chunk size
- Registry-based plugin

Future improvements:
- Chunk overlap
- Metadata
- Token-aware chunk size
"""



#separators = ["\n\n", "\n", ". ", " "]
separators = ["\n\n", "\n", ". "]
#separators = ["\n\n", "\n"]
chunk_size = 50
chunk_overlap = 0

def chunk_keep_full_word(s, l):
    chunks = []
    current_chunk = ""

    for w in s.split(" "):
        # Look ahead: See if current chunk + new word + a space exceeds the limit
        if len(current_chunk) + len(w) + 1  <= l:
            current_chunk += w + " "
        else:
            if current_chunk:  # Avoid appending an empty string on the first pass
                chunks.append(current_chunk.strip())  # .strip() removes trailing spaces
            current_chunk = w + " "

    if current_chunk:
        chunks.append(current_chunk.strip())

    return chunks

class RecursiveChunker(Chunker, chunker_type='recursive'): 
    def __init__(self, chunker_type):
        pass
    def chunk(self, segment: str):
        chunks = []
        tlist = [segment.strip()]
        for s in separators:
            tlist = [piece 
                     for t in tlist 
                        for piece in (t.split(s)
                                      if len(t) > chunk_size else [t])
                                        if piece.strip()
                     ]
        chunks += [chunk for t in tlist for chunk in chunk_keep_full_word(t, chunk_size)]
        return chunks


'''
seg = """
[Chapter 1: The AI Revolution]
Artificial intelligence is transforming software development at a rapid pace. Developers use LLMs daily. These models generate code, write tests, and document APIs efficiently. However, large documents present a unique challenge for LLMs due to context window limits.

[Section 1.1: The Need for Chunking]
To solve context limits, developers use text chunking strategies. Chunking breaks large documents into smaller pieces. A recursive chunker is highly effective because it respects natural text boundaries. It splits by paragraphs first, then sentences, and finally words.

[Section 1.2: Implementation Strategy]
Writing a recursive chunker requires a clear list of separator tokens. Typical separators include double newlines, single newlines, spaces, and empty strings. The algorithm inspects the text length recursively. If the chunk is too large, it splits again using the next separator in the hierarchy. This preserves semantic context.

"""
# module test
c = RecursiveChunker(chunker_type='recursive')
chunks = c.chunk(seg)
for i,c in enumerate(chunks,1):
    print(f'Chunk {i}')
    print(c)
    print(len(c), ' ','-' * 40)
'''
