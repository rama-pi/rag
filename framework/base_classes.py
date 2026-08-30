from abc import ABC, abstractmethod
from pathlib import Path
from builtins import RuntimeError



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

class Document(ABC):
    registry = {}

    def __init__(self, config: dict):
        self.loader = None
        self.parser = None
        self.chunker = None
        self.embedder = None
        self.pages = []

        # Loader
        loader_type = config['loader_type']
        if Loader.registry[loader_type]:
            self.loader = Loader.registry[loader_type](loader_type=loader_type)
        else:
            raise RuntimeError(
                    f"No loaddr plugin registered as {loader_type}"
                    )

        # Parser
        parser_type = config['parser_type']
        if Parser.registry[parser_type]:
            self.parser = Parser.registry[parser_type](parser_type = parser_type)
        else:
            raise RuntimeError(
                    f"No parser plugin registered as {parser_type}"
                    )

        # Chunker
        chunker_type = config['chunker_type']
        if Chunker.registry[chunker_type]:
            self.chunker = Chunker.registry[chunker_type](chunker_type=chunker_type)
        else:
            raise RuntimeError(
                    f"No chunker plugin registered as {chunker_type}"
                    )
        # Embedder
        embed_model = config['embed_model']
        if Embedder.registry[embed_model]:
            self.embedder = Embedder.registry[embed_model](embed_model=embed_model)
        else:
            raise RuntimeError(
                    f"No embedder registered as {embed_model}"
                    )
        # Storer
        storage_type = config['storage_type']
        if Storer.registry[storage_type]:
            self.storer = Storer.registry[storage_type](storage_type=storage_type, db_collection=config['storage_name'])
        else:
            raise RuntimeError(
                    f"No storer plugin registered as {storage_type}"
                    )

    @classmethod
    def open(cls, path: str|Path, config: dict):
        doc_type = Path(path).suffix.lower().lstrip(".")

        try:
            doc_cls = cls.registry[doc_type]
        except KeyError:
            raise RuntimeError(
                    f"No Document plugin registered for '{doc_type}'"
                    )
        doc = doc_cls(document_type='pdf', config=config)
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
    @abstractmethod
    def embed(self, chunks: list):
        pass
    @abstractmethod
    def store(self, chunks: list, store_vecs: list):
        pass
    def query(self, chunk: str):
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

class Chunker(ABC):
    registry = {}

    @abstractmethod
    def chunk(self, segment: str):
        pass
    def __init_subclass__(cls, chunker_type=None, **kwargs):
        super().__init_subclass__(**kwargs)
        cls.chunker_type = chunker_type
        Chunker.registry[chunker_type] = cls


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

class Embedder(ABC):
    registry = {}

    @abstractmethod
    def embed(self, chunks: list):
        pass
    def __init_subclass__(cls, embed_model=None, **kwargs):
        super().__init_subclass__(**kwargs)
        cls.embed_model = embed_model
        Embedder.registry[embed_model] = cls

class Storer(ABC):
    registry = {}

    @abstractmethod
    def store(self, chunks: list, store_vec: list):
        pass
    @abstractmethod
    def query(self, query_vec: list):
        pass
    def __init_subclass__(cls, storage_type=None, **kwargs):
        super().__init_subclass__(**kwargs)
        cls.storage_name = storage_type
        Storer.registry[storage_type] = cls

