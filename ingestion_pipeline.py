import os, sys, json, re, string
from datetime import datetime
from abc import ABC, abstractmethod
from pathlib import Path
import importlib


from framework.helpers import remove_unwanted, discover
from framework.base_classes import Document

config = {
    "wanted_model": "llama3.2",
    "wanted_mode" : "stream",
    "history_file": "history.json",
    "conversation_size": 10,
    "search_type" : "re",
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
    discover("plugins/documents/")
    discover("plugins/loaders/")
    discover("plugins/parsers/")
    discover("plugins/chunkers/")

    load_config()

    pd = Document.open("sample_chunking_text.pdf")
    pd.dump_pages()
    pd.dump_words(page=0)
    pd.dump_lines(page=0)
    pd.dump_paras(page=0)
    paras = pd.parse_paras(page=0)
    chunks = pd.chunk(paras[-1])
    for i,c in enumerate(chunks,1):
        print(f'Chunk {i}')
        print(c)
        print(len(c), ' ','-' * 40)

if __name__ == "__main__":
    main()


