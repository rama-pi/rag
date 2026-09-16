from pathlib import Path
import struct

from framework.base_classes import Document
from framework.base_classes import Loader
from framework.base_classes import Parser
from framework.base_classes import Chunker
from framework.base_classes import Embedder
from framework.base_classes import Storer


class PdfDocument(Document, document_type='pdf'):
    def __init__(self, document_type: str, config: dict):
        super().__init__(config)
    def load(self, path: str|Path):
        self.pages = self.loader.load(path)
    def dump_words(self, page: int):
        self.parser.dump_words(self.pages[page])
    def parse_words(self, page: int):
        self.parser.dump_words(self.pages[page])
    def dump_lines(self, page: int):
        self.parser.dump_lines(self.pages[page])
    def parse_lines(self, page: int):
        return self.parser.parse_lines(self.pages[page])
    def dump_paras(self, page: int):
        self.parser.dump_paras(self.pages[page])
    def parse_paras(self, page: int):
        return self.parser.parse_paras(self.pages[page])
    def dump_pages(self):
        self.parser.dump_pages(self.pages)
    def chunk(self, segment: str):
        return self.chunker.chunk(segment)
    def store_document(self, document_name: str):
        return self.storer.store_document(document_name)
    def store_chunks(self, doc_id: int, chunks: list):
        return self.storer.store_chunks(doc_id, chunks)
    def get_chunks(self, doc_id: int | None = None):
        return self.storer.get_chunks(doc_id)
    def store_embedding(self, vecs: list):
        self.embedders['nomic-embed-text'].embed(vec)
        return
    def store_and_embed_chunks(self, doc_id: int, chunks: list):
        # store chunks, make embedding per chunk, store chunk's embedding
        # model name of the embedder
        model_name = self.config["dense_embedder"]["model_name"]
        for chunk in chunks:
            #store chunk
            chunk_id = self.storer.store_chunk(doc_id, chunk)
            embedding = self.embedders[model_name].embed(chunk)
            #store embedding
            self.storer.store_vector(chunk_id, embedding.embeddings[0])
        return
    '''
    def embed(self, chunks: list):
        embeddings = {} # key = embed model value = embedding/s
        for name,embedder in self.embedders.items():
            embeddings[name] = embedder.embed(chunks)
        return embeddings
    '''
    def query(self, chunk: str):
        # get chunks, entire corpus
        # [ (chunk_id, doc_id, chunk), ... ]
        chunks = get_chunks()
        #get BM25 embedding per chunk
        chunk_vocab_score = []
        for chunk in chunks:
            chunk_vocab_score.append({chunk[0]: self.embedders['BM25'].embed(chunk[2])})
    def preprocess(self, chunk: str):
        return self.preprocessor.preprocess(chunk)

