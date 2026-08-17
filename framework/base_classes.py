from abc import ABC, abstractmethod
from pathlib import Path

class Page():
    def __init__(self):
        self.page_number = 0
        self.width = 0
        self.height = 0
        self.rotation = 0

        self.words = []
        self.lines = []
        self.paragraphs = []
        self.chunks = []
        self.embeddings = []
        self.images = []
        self.tables = []
        self.annotations = []
        self.metadata = {}

class Model(ABC):
    registry = {}

    @abstractmethod
    def ask(self, question: str):
        pass
    def __init_subclass__(cls, model_name=None, model_modes=None, **kwargs):
        super().__init_subclass__(**kwargs)
        cls.model_name = model_name
        cls.model_modes = model_modes
        Model.registry[model_name] = cls

class Chunker(ABC):
    registry = {}

    @abstractmethod
    def chunk(self, segment: str):
        pass
    def __init_subclass__(cls, chunker_type=None, **kwargs):
        super().__init_subclass__(**kwargs)
        cls.chunker_type = chunker_type
        Chunker.registry[chunker_type] = cls

class Document(ABC):
    registry = {}

    @classmethod
    def open(cls, path: str|Path):
        doc_type = Path(path).suffix.lower().lstrip(".")

        try:
            doc_cls = cls.registry[doc_type]
        except KeyError:
            raise RunTimeError(
                    f"No Document plugin registered for '{doc_type}'"
                    )
        doc = doc_cls(document_type='pdf')
        doc.load(path)
        return doc
    @abstractmethod
    def load(self, path: str|Path):
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
    def dump_pages(self):
        pass
    @abstractmethod
    def chunk(self, segment: str):
        pass

    def __init_subclass__(cls, document_type=None, **kwargs):
        super.__init_subclass__(**kwargs)
        cls.document_type = document_type
        Document.registry[document_type] = cls

class Loader(ABC):
    registry = {}

    @abstractmethod
    def load(self, segment: str):
        pass
    def __init_subclass__(cls, loader_type=None, **kwargs):
        super().__init_subclass__(**kwargs)
        cls.loader_type = loader_type
        Loader.registry[loader_type] = cls

class Parser(ABC):
    registry = {}

    @abstractmethod
    def parse_words(self, page: Page):
        pass
    @abstractmethod
    def dump_words(self, page: Page):
        pass
    @abstractmethod
    def parse_lines(self, page: Page):
        pass
    @abstractmethod
    def dump_lines(self, page: Page):
        pass
    @abstractmethod
    def parse_paras(self, page: Page):
        pass
    @abstractmethod
    def dump_paras(self, page: Page):
        pass
    @abstractmethod
    def dump_pages(self, pages: list[Page]):
        pass
    def __init_subclass__(cls, parser_type=None, **kwargs):
        super().__init_subclass__(**kwargs)
        cls.parser_type = parser_type
        Parser.registry[parser_type] = cls

'''
User Query
      │
      ▼
QueryPreprocessor
      │
      ├── tokenize
      ├── lowercase
      ├── lemmatize
      ├── synonym expansion
      ▼
Processed Query
      │
      ▼
Retriever
      │
      ├── KeywordRetriever
      ├── RegexRetriever
      └── (later) VectorRetriever
'''
class PreProcessor(ABC):
    registry = {}

    @abstractmethod
    def load(self, segment: str):
        pass
    def __init_subclass__(cls, preprocessor_type=None, **kwargs):
        super().__init_subclass__(**kwargs)
        cls.loader_type = preocesor_type
        PreProcessor.registry[preprocessor_type] = cls


class Retriever(ABC):
    registry = {}

    @abstractmethod
    def retrieve(self, past_q_w: list, curr_q_w: list):
        pass
    def __init_subclass__(cls, retriever_name=None, **kwargs):
        super().__init_subclass__(**kwargs)
        cls.retriever_name = retriever_name
        Retriever.registry[retriever_name] = cls


