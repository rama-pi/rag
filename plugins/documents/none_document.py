from pathlib import Path
import struct

from framework.base_classes import Document
from framework.base_classes import Loader
from framework.base_classes import Parser
from framework.base_classes import Chunker
from framework.base_classes import Embedder
from framework.base_classes import Storer


class NoneDocument(Document, document_type='None'):
    def __init__(self, document_type: str, config: dict):
        return super().__init__(config)
    @abstractmethod
    def transaction(self):
        pass

    @abstractmethod
    def dump_words(self, page: int):
        pass
    @abstractmethod
    def parse_words(self, page: int):
        pass
    @abstractmethod
    def dump_lines(self, page: int):
        pass
    @abstractmethod
    def parse_lines(self, page: int):
        pass
    @abstractmethod
    def dump_paras(self, page: int):
        pass
    @abstractmethod
    def parse_paras(self, page: int):
        pass
    @abstractmethod
    def get_page_numbers(self):
        pass
    @abstractmethod
    def dump_pages(self):
        pass

    @abstractmethod
    def preprocess(self, chunk: str):
        pass

    @abstractmethod
    def get_file_meta(self):
        pass
    @abstractmethod
    def get_file_hash(self):
        pass

    @abstractmethod
    def store_document(self, document_name: str, mdata: str, fhash: str):
        pass
    @abstractmethod
    def chunk(self, segment: str):
        pass
     def get_chunks(self, doc_id: int | None = None):
         return super().get_chunks(doc_id)
     def retrieve(self, chunk: str):
         return super.retrieve(chunk)



