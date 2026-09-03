import os, sys, json, re, string
from datetime import datetime
from abc import ABC, abstractmethod
from pathlib import Path
import importlib


from framework.helpers import discover
from framework.base_classes import Document

config = {
    "wanted_model"     : "llama3.2",
    "sparse_embedder": {
        "engine": "BM25",
        "parameters": {
            "k1": 1.2,
            "b": 0.75
            }
        },
    "dense_embedder": {
        "model_name": "nomic-embed-text",
        "dimensions": 768
        },
    "storage_type"     : "sqlite",
    "storage_name"     : "rag_collection.db",
    "wanted_mode"      : "stream",
    "history_file"     : "history.json",
    "conversation_size": 10,                # limit to smaller than models context window size
    "search_type"      : "re",
    "loader_type"      : "pdf",
    "parser_type"      : "pdf",
    "chunker_type"     : "recursive",
    "preprocessor_type": "preprocess",
}

def load_config():
    global config
    try:
        with open("config.json", 'r') as cf:
            config = json.load(cf)
    except FileNotFoundError:
        with open("config.json", 'w') as cf:
            json.dump(config, cf, indent=4)
        print("""
              No configuration file found.
              Created config.json using default settings.
              Please review the file and run the program again.
              """)
        sys.exit(1)
    except:
        print(f"An error occurred:")
        sys.exit(1)


# Main
#user / Composition Root / Main
def main():
    #discover plugins
    discover("plugins/models")
    discover("plugins/documents/")
    discover("plugins/loaders/")
    discover("plugins/parsers/")
    discover("plugins/preprocessors")
    discover("plugins/chunkers/")
    discover("plugins/embedders/")
    discover("plugins/storers/")
    discover("plugins/retrievers")

    load_config()

    pd = Document.open("sample_chunking_text.pdf", config)
    paras = pd.parse_paras(page=0)
    chunks = pd.chunk(paras[-1])
    chunks = [pd.preprocess(chunk) for chunk in chunks]
    vecs = pd.embed(chunks)
    print(vecs)
    #pd.store(chunks, vecs)
    #closest_chunks = pd.query("The landscape of modern technology changed permanently")
    #print(closest_chunks)


if __name__ == "__main__":
    main()
