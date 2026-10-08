from abc import ABC, abstractmethod
from pathlib import Path
from builtins import RuntimeError
import json



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

    def __init_subclass__(cls, document_type=None, **kwargs):
        # this runs earlier that __init__
        super.__init_subclass__(**kwargs)
        cls.document_type = document_type
        Document.registry[document_type] = cls

    def __init__(self, config: dict):
        self.loader = None
        self.parser = None
        self.chunker = None
        self.preprocessor = None
        self.embedders = {}
        self.retrievers = []
        self.pages = []
        self.config = config

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
        # preprocessor
        preprocessor_type = config["preprocessor_type"]
        if PreProcessor.registry[preprocessor_type]:
            self.preprocessor = PreProcessor.registry[preprocessor_type](preprocessor_type=preprocessor_type)
        else:
            raise RuntimeError(
                    f"No preprocessor plugin registered as {preprocessor_type}"
                    )

        # Chunker
        chunker_type = config['chunker_type']
        if Chunker.registry[chunker_type]:
            self.chunker = Chunker.registry[chunker_type](chunker_type=chunker_type)
        else:
            raise RuntimeError(
                    f"No chunker plugin registered as {chunker_type}"
                    )
        # Embedders
        engine = config["sparse_embedder"]["engine"]
        if Embedder.registry[engine]:
            self.embedders[engine] = Embedder.registry[engine](engine)
        else:
            raise RuntimeError(
                    f"No embedder registered as {engine}"
                    )
        model_name = config["dense_embedder"]["model_name"]
        if Embedder.registry[model_name]:
            self.embedders[model_name] = Embedder.registry[model_name](model_name)
        else:
            raise RuntimeError(
                    f"No embedder registered as {model_name}"
                    )
        # Storer
        storage_type = config['storage_type']
        if Storer.registry[storage_type]:
            self.storer = Storer.registry[storage_type](storage_type=storage_type, db_collection=config['storage_name'])
        else:
            raise RuntimeError(
                    f"No storer plugin registered as {storage_type}"
                    )
        # Retrievers
        retrievers = config["cosine_similarity_retrievers"]
        for retriever in retrievers:
            if Retriever.registry[retriever['name']]:
                self.retrievers.append({
                    'retriever':Retriever.registry[retriever['name']](retriever_name=retriever['name']),
                    'type':retriever['type']
                    })
            else:
                raise RuntimeError(
                        f"No retriever plugin registered as {retriever}"
                        )


    @classmethod
    def open(cls, path: str|Path, config: dict):

        """
            support of doc type None for access to api
        """
        if path is None:
            doc_type = "null"
        else:
            doc_type = Path(path).suffix.lower().lstrip(".")

        try:
            doc_cls = cls.registry[doc_type]
        except KeyError:
            raise RuntimeError(
                    f"No Document plugin registered for '{doc_type}'"
                    )

        doc = doc_cls(document_type=doc_type, config=config)
        if path is not None:
            # load the document
            doc.load(path)

        return doc
    @abstractmethod
    def load(self, path: str|Path):
        pass

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
    def get_document(self, doc_id : int):
        return self.storer.get_document(doc_id)
    @abstractmethod
    def chunk(self, segment: str):
        pass
    @abstractmethod
    def store_chunks(self, doc_id: int, chunks: list):
        '''
        pass
        '''
        return self.storer.store_chunks(doc_id, chunks)
    @abstractmethod
    def get_chunks(self, doc_id: int | None = None, chunk_id: int | None = None):
        '''
        pass
        '''
        return self.storer.get_chunks(doc_id, chunk_id)

    @abstractmethod
    def store_and_embed_chunks(self, doc_id: int, chunks: list):
        # store chunks, make embedding (dense) per chunk, store chunk's embedding
        # model name of the embedder
        model_name = self.config["dense_embedder"]["model_name"]
        for chunk in chunks:
            #store chunk
            chunk_id = self.storer.store_chunk(doc_id, chunk)
            #create embedding
            embedding = self.embedders[model_name].embed(chunk)
            #store embedding
            self.storer.store_vector(chunk_id, embedding.embeddings[0])
        return
    @abstractmethod
    def retrieve(self, qchunk: str, top_n: int):
        '''
        pass
        '''
        qembed = None
        # retrieve all chunks
        # [(chunk_id, doc_id, chunk), (chunk_id, doc_id, chunk)]
        doc_chunks = self.storer.get_chunks()
        # retrieve all nomic embeddings
        doc_embeds = self.storer.get_vectors()
        # dense embed the qchunk
        for name,embedder in self.embedders.items():
            if name == "nomic-embed-text":
                qembed = embedder.embed(qchunk)['embeddings'][0]
        # call each type retriever, each returns a score against the query chunk
        for retriever in self.retrievers:
            if retriever['type'] == 'sparse':
                cs_ordered_score1 = retriever['retriever'].retrieve(qchunk, doc_chunks, top_n)
            if retriever['type'] == 'dense':
                cs_ordered_score2 = retriever['retriever'].retrieve(qembed, doc_embeds, doc_chunks, top_n)
        # rrf 
        # collect chunk ids from each retriever
        k = self.config["rrf_smoothing_param"]

        chunk_ids1 = set((i[0] for i in cs_ordered_score1))
        chunk_ids2 = set((i[0] for i in cs_ordered_score2))
        chunks = set()
        for e in cs_ordered_score1:
            chunks.add((e[0],e[1]['doc_id']))
        for e in cs_ordered_score2:
            chunks.add((e[0],e[1]['doc_id']))


        rank_list = []
        #do rrf for chunks in both
        for cid in chunk_ids1 & chunk_ids2:
            r1 = [e for e, i in enumerate(cs_ordered_score1, start=1) if i[0] == cid][0]
            r2 = [e for e, i in enumerate(cs_ordered_score2, start=1) if i[0] == cid][0]
            rrf = 1.0/(k+r1) + 1.0/(k+r2)
            rank_list.append(
                    {'cid': cid,
                     'rrf': rrf
                     }
                    )
        # do rrf for chunks in only one
        for cid in chunk_ids1-chunk_ids2:
            r1 = [e for e, i in enumerate(cs_ordered_score1, start=1) if i[0] == cid][0]
            rrf = 1.0/(k+r1)
            rank_list.append(
                    {'cid': cid,
                     'rrf': rrf
                     }
                    )
        # do rrf for chunks in only one
        for cid in chunk_ids2-chunk_ids1:
            r2 = [e for e, i in enumerate(cs_ordered_score2, start=1) if i[0] == cid][0]
            rrf = 1.0/(k+r2)
            rank_list.append(
                    {'cid': cid,
                     'rrf': rrf
                     }
                    )
        # add in doc id's
        chunk_map = {c[0]: c[1] for c in chunks}
        _ = [r.update({'doc_id': chunk_map[r['cid']]}) for r in rank_list if r['cid'] in chunk_map]
        # sort the rakings of the chunsk
        rank_list = sorted(rank_list, key=lambda d: d['rrf'], reverse=True )
        return rank_list

    '''
    @abstractmethod
    def query(self, chunk: str):
        pass
    '''


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
    def preprocess(self, segment: str):
        pass
    def __init_subclass__(cls, preprocessor_type=None, **kwargs):
        super().__init_subclass__(**kwargs)
        cls.loader_type = preprocessor_type
        PreProcessor.registry[preprocessor_type] = cls

class Retriever(ABC):
    registry = {}

    def __init_subclass__(cls, retriever_name=None, **kwargs):
        super().__init_subclass__(**kwargs)
        cls.retriever_name = retriever_name
        Retriever.registry[retriever_name] = cls
    @abstractmethod
    def retrieve(self, past_q_w: list, curr_q_w: list):
        pass

class Embedder(ABC):
    registry = {}

    @abstractmethod
    def embed(self, chunk: str):
        pass
    def __init_subclass__(cls, embed_model=None, **kwargs):
        super().__init_subclass__(**kwargs)
        cls.embed_model = embed_model
        Embedder.registry[embed_model] = cls

class Storer(ABC):
    registry = {}

    @abstractmethod
    def store_document(self, document_name: str, metadata: str, file_content_hash: str):
        pass
    def get_document(self, doc_id):
        pass
    @abstractmethod
    def store_chunk(self, doc_id: int, chunk: str) -> int:
        pass
    @abstractmethod
    def get_chunks(self, doc_id: int | None = None):
        pass
    def store_vector(self, chunk_id: int, vec: list) -> None:
        pass
    @abstractmethod
    def get_vector(self, chunk_id: int) -> list:
        pass
    @abstractmethod
    def get_vectors(self):
        pass
    def transaction(self):
        pass
    '''
    @abstractmethod
    def begin(self):
        # begin a transaction
        pass
    def finalize(self):
        # commit a transaction
        pass
    def abort(self):
        # abort a transaction
        pass
    '''
    def __init_subclass__(cls, storage_type=None, **kwargs):
        super().__init_subclass__(**kwargs)
        cls.storage_name = storage_type
        Storer.registry[storage_type] = cls

