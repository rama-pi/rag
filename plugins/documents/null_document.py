from pathlib import Path
import struct

from framework.base_classes import Document
from framework.base_classes import Loader
from framework.base_classes import Parser
from framework.base_classes import Chunker
from framework.base_classes import Embedder
from framework.base_classes import Storer


class NullDocument(Document, document_type='null'):
    def __init__(self, document_type: str, config: dict):
        return super().__init__(config)

    '''
        not allowed on null document
    '''
    def load(self, path: str|Path):
        pass
    def transaction(self):
        pass
    def dump_words(self, page: int):
        pass
    def parse_words(self, page: int):
        pass
    def dump_lines(self, page: int):
        pass
    def parse_lines(self, page: int):
        pass
    def dump_paras(self, page: int):
        pass
    def parse_paras(self, page: int):
        pass
    def get_page_numbers(self):
        pass
    def dump_pages(self):
        pass
    def preprocess(self, chunk: str):
        pass
    def get_file_meta(self):
        pass
    def get_file_hash(self):
        pass
    def store_document(self, document_name: str, mdata: str, fhash: str):
        pass
    def chunk(self, segment: str):
        pass
    def store_chunks(self, doc_id: int, chunks: list):
        pass
    def get_chunks(self, doc_id: int | None = None):
        pass
    def store_document(self, document_name: str, mdata: str, fhash: str):
        pass
    def store_and_embed_chunks(self, doc_id: int, chunks: list):
        pass

    '''
        Allowed on none document
    '''
    def retrieve(self, chunk: str, top_n: int):
        return super().retrieve(chunk, top_n)



