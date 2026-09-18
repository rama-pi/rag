import os, sys, json, re, string, json
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
    "ingest_docs"      : "./ingest_docs"
}

# keep opened docs  their id, name, onj
docs = []
# global stats
total_documents = 0
total_paras  = 0
total_pages = 0
total_chunks = 0


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

# similar to llama_index.core::SimpleDirectoryReader
def ingest():
    global total_documents, total_pages, total_paras, total_chunks

    ingest_subfolder = "./ingestion_docs"
    # 1. Convert the folder path to a proper path object relative to project root
    base_path = Path(ingest_subfolder)
    if not base_path.exists():
        print(f"[Framework Warning] Ingest directory {ingest_subfolder} not found.")
        return

    # 3. Iterate over every entry in the directory
    for entry in os.listdir(base_path):
        # Skip hidden files (like .DS_Store), private files (__init__.py), and directories
        if entry.startswith('.') or entry.startswith('__') or not entry.endswith('.pdf'):
            continue
        full_path = os.path.join(base_path, entry)
        if os.path.isfile(full_path):
            doc = Document.open(full_path, config)
            mdata = json.dumps(doc.get_file_meta())
            fhash  = doc.get_file_hash()
            doc_id = doc.store_document(full_path, mdata, fhash)
            if doc_id is None:
                # doc already ingested
                continue
            total_documents += 1
            page_numbers = doc.get_page_numbers()
            total_pages += len(page_numbers)
            for page_number in page_numbers:
                paras = doc.parse_paras(page=page_number)
                total_paras += len(paras)
                for para in paras:
                    chunks = doc.chunk(para)
                    chunks = [doc.preprocess(chunk) for chunk in chunks]
                    total_chunks += len(chunks)
                    doc.store_and_embed_chunks(doc_id, chunks)
            docs.append({'doc': doc, 'id': doc_id, 'name': full_path})
    
    for doc in docs:
        print(doc)
    print(f"Document count {total_documents} Pages count {total_pages} Paragraphs count {total_paras} Chunks count {total_chunks}")

    return


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

    ingest()

if __name__ == "__main__":
    main()
