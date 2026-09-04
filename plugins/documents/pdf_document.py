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
    def embed(self, chunks: list):
        embeddings = {}
        for name,embedder in self.embedders.items():
            embeddings[name] = embedder.embed(chunks)
        return embeddings
    def store_document(self, document_name: str):
        return self.storer.store_document(document_name)
    def store(self, chunks: list, store_vecs: list):
        return self.storer.store(chunks, store_vecs)
    def query(self, chunk: str):
        q_v = self.embedder.embed(chunk)
        q_v = struct.pack(
                f"{len(q_v.embeddings[0])}f",
                *q_v.embeddings[0]
                )
        return self.storer.query(q_v)
    def preprocess(self, chunk: str):
        return self.preprocessor.preprocess(chunk)

