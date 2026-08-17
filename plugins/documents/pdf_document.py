from pathlib import Path

from framework.base_classes import Document
from framework.base_classes import Loader
from framework.base_classes import Parser
from framework.base_classes import Chunker

'''
from loader import Loader
from parser import Parser
from chunker import Chunker
'''

class PdfDocument(Document, document_type='pdf'):
    def __init__(self, document_type):
        self.loader = None
        self.parser = None
        self.pages = []

        if Loader.registry["pdf"]:
            self.loader = Loader.registry["pdf"](loader_type="pdf")
        else:
            raise RunTimeError(
                    f"No loaddr plugin registered as pdf"
                    )
        if Parser.registry["pdf"]:
            self.parser = Parser.registry["pdf"](parser_type="pdf")
        else:
            raise RunTimeError(
                    f"No parser plugin registered as pdf"
                    )
        if Chunker.registry["recursive"]:
            self.chunker = Chunker.registry["recursive"](chunker_type="recursive")
        else:
            raise RunTimeError(
                    f"No chunker plugin registered as recursive"
                    )
            return
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
